from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import Integer
from database import init_db, SessionLocal, Player, PlayerStats
from models import PlayerResponse, PlayerDetailedResponse, PaginatedPlayerResponse, IntegrationReportResponse, TacticalDNAResponse, PlayerStatsResponse, AITwinResponse
from ingestion import run_ingestion
from scraper import get_market_value
import json
import math

from fastapi.middleware.cors import CORSMiddleware
from security import verify_api_key
from database import APIKey

app = FastAPI(title="Football Scouting API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()
    db = SessionLocal()
    try:
        if db.query(APIKey).count() == 0:
            seed_key = APIKey(key="super-secret-admin-key", role="admin")
            db.add(seed_key)
            db.commit()
    finally:
        db.close()
    
    # Pre-load position index so the dropdown works immediately
    from ingestion import build_position_ledger, determine_positions, load_advanced_metrics
    import ingestion
    from collections import defaultdict
    
    load_advanced_metrics()
    ledger, positions = build_position_ledger("./Date - meciuri")
    ingestion._global_discovered_positions = positions
    
    # Build search index using only validated (noise-filtered) positions
    search_index = defaultdict(list)
    for pid, pos_data in ledger.items():
        validated = determine_positions(pos_data)
        valid_codes = set()
        if validated["primary"]:
            valid_codes.add(validated["primary"]["code"])
        for sec in validated["secondary"]:
            valid_codes.add(sec["code"])
        for code in valid_codes:
            search_index[code.lower()].append(pid)
    ingestion._global_search_index = dict(search_index)
    
    print(f"Startup: Loaded {len(positions)} positions, {len(ingestion._global_search_index)} index groups (noise-filtered).")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health_check():
    """Quick health check — no auth required."""
    return {"status": "ok"}

# ═══════════════════════ Authentication ═══════════════════════
from pydantic import BaseModel as PydanticBase

class LoginRequest(PydanticBase):
    email: str
    password: str

@app.post("/api/v1/auth/login")
def login(req: LoginRequest):
    """Hardcoded admin login — single manager account."""
    if req.email == "manager@ucluj.ro" and req.password == "1234":
        return {"success": True, "token": "ucluj-admin-token-777"}
    raise HTTPException(status_code=401, detail="Email sau parolă incorectă.")

@app.get("/api/v1/positions")
def get_positions(api_key: APIKey = Depends(verify_api_key)):
    from ingestion import get_global_discovered_positions
    return get_global_discovered_positions()

@app.get("/api/v1/search-index")
def get_search_index(api_key: APIKey = Depends(verify_api_key)):
    from ingestion import get_global_discovered_positions, get_global_search_index
    return {
        "availableFilters": get_global_discovered_positions(),
        "positionGroups": get_global_search_index()
    }

@app.post("/api/v1/system/ingest")
def trigger_ingestion(db: Session = Depends(get_db), api_key: APIKey = Depends(verify_api_key)):
    try:
        run_ingestion(db)
        return {"message": "Data ingestion and processing completed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/scout/search", response_model=PaginatedPlayerResponse)
def search_players(
    position: str = Query(None),
    max_price: int = Query(None),
    min_price: int = Query(None),
    min_score: float = Query(None),
    age_min: int = Query(None),
    age_max: int = Query(None),
    name: str = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1),
    db: Session = Depends(get_db),
    api_key: APIKey = Depends(verify_api_key)
):
    from sqlalchemy import func
    from database import MarketValueCache
    
    # 1. Base Query with Joins
    query = db.query(Player, PlayerStats, MarketValueCache.market_value)\
        .outerjoin(PlayerStats, Player.wyId == PlayerStats.wyId)\
        .outerjoin(MarketValueCache, Player.wyId == MarketValueCache.wyId)
    
    # 2. Database-Level Filters
    if position:
        query = query.filter(Player.positionCode.ilike(position))
        
    if min_score is not None:
        query = query.filter(PlayerStats.performance_score >= min_score)
        
    # Diacritic-insensitive name search
    # SQLite ILIKE can't strip accents, so we handle it in Python
    _name_query_normalized = None
    if name:
        import unicodedata
        _name_query_normalized = unicodedata.normalize('NFD', name.lower())
        _name_query_normalized = ''.join(
            c for c in _name_query_normalized if unicodedata.category(c) != 'Mn'
        )
        
    if max_price is not None:
        query = query.filter(MarketValueCache.market_value <= max_price)
    if min_price is not None:
        query = query.filter(MarketValueCache.market_value >= min_price)
        
    if age_min is not None or age_max is not None:
        # SQLite Age Calculation: current_year - birth_year
        # Assuming birthDate is 'YYYY-MM-DD'
        birth_year = func.substr(Player.birthDate, 1, 4)
        current_year = func.strftime('%Y', 'now')
        age_expr = current_year.cast(Integer) - birth_year.cast(Integer)
        
        if age_min is not None:
            query = query.filter(age_expr >= age_min)
        if age_max is not None:
            query = query.filter(age_expr <= age_max)

    # 3. Pagination & Execution
    # Default sort by performance score DESC
    query = query.order_by(PlayerStats.performance_score.desc().nullslast())

    # If name search is active, we do Python-level accent-folded matching
    # because SQLite ILIKE cannot strip diacritics.
    if _name_query_normalized:
        import unicodedata as _ud
        def _normalize(s):
            if not s: return ""
            return ''.join(c for c in _ud.normalize('NFD', s.lower()) if _ud.category(c) != 'Mn')

        # Fetch all rows (other SQL filters still apply) and filter in Python
        all_results = query.all()
        filtered = []
        for player, stats, market_val in all_results:
            full = _normalize(f"{player.firstName or ''} {player.lastName or ''}")
            short = _normalize(player.shortName or "")
            if _name_query_normalized in full or _name_query_normalized in short:
                filtered.append((player, stats, market_val))

        total_players = len(filtered)
        skip = (page - 1) * limit
        db_results = filtered[skip : skip + limit]
    else:
        # No name filter — efficient SQL path
        total_players = query.count()
        skip = (page - 1) * limit
        db_results = query.offset(skip).limit(limit).all()

    # 4. Build Response
    data = []
    for player, stats, market_val in db_results:
        # Extract tacticalProfile if exists in JSON
        tactical_profile = None
        if stats and stats.normalized_stats:
            try:
                ns = json.loads(stats.normalized_stats)
                tactical_profile = ns.get('tacticalProfile')
            except:
                pass

        # Enrich with Transfermarkt data from CSV
        from csv_lookup import player_match_optimizer
        tm_data = player_match_optimizer(player.firstName or '', player.lastName or '')
        
        data.append(PlayerResponse(
            wyId=player.wyId,
            shortName=player.shortName,
            firstName=player.firstName,
            lastName=player.lastName,
            birthDate=player.birthDate,
            positionCode=player.positionCode,
            minutesOnField=stats.minutesOnField if stats else 0,
            performance_score=stats.performance_score if stats else 0.0,
            market_value=market_val or tm_data.get('market_value_raw'),
            photoUrl=tm_data.get('image_url'), 
            club=tm_data.get('tm_club'),
            foot=tm_data.get('foot'),
            nationality=tm_data.get('nationality'),
            contractExpiration=tm_data.get('contract_expiration'),
            tacticalProfile=tactical_profile
        ))
        
    return {
        "data": data,
        "meta": {
            "totalPlayers": total_players,
            "currentPage": page,
            "totalPages": math.ceil(total_players / limit) if limit > 0 else 0
        }
    }

@app.get("/api/v1/players/{id}", response_model=PlayerDetailedResponse)
def get_player_details(id: int, db: Session = Depends(get_db), api_key: APIKey = Depends(verify_api_key)):
    player = db.query(Player).filter(Player.wyId == id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
        
    stats = db.query(PlayerStats).filter(PlayerStats.wyId == id).first()
        
    # Use CSV lookup instead of external API
    from csv_lookup import player_match_optimizer
    search_name = f"{player.firstName} {player.lastName}".strip()
    if not search_name:
        search_name = player.shortName
    
    csv_result = player_match_optimizer(player.firstName or '', player.lastName or '')
    market_val = int(csv_result['market_value_raw']) if csv_result.get('market_value_raw') else None
    
    normalized_stats_dict = {}
    if stats and stats.normalized_stats:
        normalized_stats_dict = json.loads(stats.normalized_stats)
        
    return PlayerDetailedResponse(
        wyId=player.wyId,
        shortName=player.shortName,
        firstName=player.firstName,
        lastName=player.lastName,
        birthDate=player.birthDate,
        positionCode=player.positionCode,
        minutesOnField=stats.minutesOnField if stats else 0,
        performance_score=stats.performance_score if stats else 0.0,
        market_value=market_val,
        photoUrl=csv_result.get('image_url'),
        club=csv_result.get('tm_club'),
        foot=csv_result.get('foot'),
        nationality=csv_result.get('nationality'),
        contractExpiration=csv_result.get('contract_expiration'),
        normalized_stats=normalized_stats_dict
    )

@app.get("/api/v1/players/{id}/transfermarkt")
def get_player_transfermarkt(id: int, db: Session = Depends(get_db), api_key: APIKey = Depends(verify_api_key)):
    """Lazy-loaded CSV lookup for Transfermarkt data (image + market value)."""
    player = db.query(Player).filter(Player.wyId == id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    from csv_lookup import player_match_optimizer, get_transfer_history
    result = player_match_optimizer(player.firstName or '', player.lastName or '')
    transfers = get_transfer_history(result.get('player_id'))
    
    return {
        "found": result['found'],
        "image_url": result.get('image_url'),
        "market_value_raw": result.get('market_value_raw'),
        "market_value_formatted": result.get('market_value_formatted'),
        "tm_name": result.get('tm_name', ''),
        "tm_club": result.get('tm_club', ''),
        "nationality": result.get('nationality'),
        "foot": result.get('foot'),
        "height_cm": result.get('height_cm'),
        "transfers": transfers
    }

@app.get("/api/v1/players/{id}/integration-report", response_model=IntegrationReportResponse)
def get_player_integration_report(id: int, db: Session = Depends(get_db), api_key: APIKey = Depends(verify_api_key)):
    """AI-driven accommodation risk and personality assessment."""
    from ai_engine import generate_integration_report
    report = generate_integration_report(id, db)
    if not report:
        raise HTTPException(status_code=404, detail="Player or data not found")
    return report

@app.get("/api/v1/players/{id}/tactical-dna", response_model=TacticalDNAResponse)
def get_player_tactical_dna(id: int, db: Session = Depends(get_db), api_key: APIKey = Depends(verify_api_key)):
    """Evaluate player against U Cluj Tactical DNA based on position."""
    from ai_engine import generate_tactical_dna
    report = generate_tactical_dna(id, db)
    if not report or not report.get("tacticalEvaluation"):
        raise HTTPException(status_code=404, detail="Player or stats not found")
    return report
_stats_df_cache = None

@app.get("/api/v1/players/{id}/stats", response_model=PlayerStatsResponse)
def get_player_stats(id: int, db: Session = Depends(get_db), api_key: APIKey = Depends(verify_api_key)):
    global _stats_df_cache
    import pandas as pd
    import json
    
    player = db.query(Player).filter(Player.wyId == id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
        
    stats = db.query(PlayerStats).filter(PlayerStats.wyId == id).first()
    
    if _stats_df_cache is None:
        try:
            _stats_df_cache = pd.read_pickle("processed_metrics.pkl")
            _stats_df_cache.set_index('wyId', inplace=True)
        except Exception:
            _stats_df_cache = pd.DataFrame()
            
    goals, assists, clean_sheets, yellow, red = 0, 0, 0, 0, 0
    if not _stats_df_cache.empty and id in _stats_df_cache.index:
        row = _stats_df_cache.loc[id]
        goals = int(row.get('total_goals', 0)) if 'total_goals' in row else 0
        assists = int(row.get('total_assists', 0)) if 'total_assists' in row else 0
        clean_sheets = int(row.get('total_gkCleanSheets', 0)) if 'total_gkCleanSheets' in row else 0
        yellow = int(row.get('total_yellowCards', 0)) if 'total_yellowCards' in row else 0
        red = int(row.get('total_directRedCards', 0)) if 'total_directRedCards' in row else 0

    radar_scores = {"Shooting": 50, "Passing": 50, "Dribbling": 50, "Defending": 50, "Physicality": 50, "Mentality": 50}
    if stats and stats.normalized_stats:
        stats_json = json.loads(stats.normalized_stats)
        radar_scores = stats_json.get('radarScores', radar_scores)

    return PlayerStatsResponse(
        goals=goals,
        assists=assists,
        cleanSheets=clean_sheets,
        yellowCards=yellow,
        redCards=red,
        radarScores=radar_scores
    )


@app.get("/api/v1/scout/ai-twin", response_model=AITwinResponse)
def get_ai_twin(query: str, db: Session = Depends(get_db), api_key: APIKey = Depends(verify_api_key)):
    from ai_engine import find_ai_twins
    result = find_ai_twins(query, db)
    if not result:
        raise HTTPException(status_code=404, detail="No matching player found or not enough data.")
    return result

from pydantic import BaseModel

class AISearchRequest(BaseModel):
    query: str

@app.post("/api/v1/scout/ai-search")
def ai_search(req: AISearchRequest, db: Session = Depends(get_db), api_key: APIKey = Depends(verify_api_key)):
    from nlp_scout import ai_scout_search
    try:
        return ai_scout_search(req.query, db)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

class AssistantRequest(BaseModel):
    wyId: int = None
    playerName: str = None
    query: str

@app.post("/api/v1/scout/assistant")
def scout_assistant(req: AssistantRequest, db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
    from ai_engine import generate_scouting_report
    try:
        wyId = req.wyId
        if not wyId and req.playerName:
            # Try to find player by name - search each word
            name_parts = req.playerName.strip().split()
            
            # First try exact full-name match
            search_str = f"%{req.playerName}%"
            player = db.query(Player).filter(
                (Player.shortName.ilike(search_str)) |
                (Player.firstName.ilike(search_str)) |
                (Player.lastName.ilike(search_str))
            ).first()
            
            # If not found, try matching individual words (e.g. "Dan Nistor" -> lastName LIKE %Nistor%)
            if not player and len(name_parts) > 1:
                from sqlalchemy import or_
                conditions = []
                for part in name_parts:
                    part_str = f"%{part}%"
                    conditions.extend([
                        Player.shortName.ilike(part_str),
                        Player.firstName.ilike(part_str),
                        Player.lastName.ilike(part_str)
                    ])
                # Find all candidates and pick the one matching the most words
                candidates = db.query(Player).filter(or_(*conditions)).all()
                
                # Score each candidate by how many name_parts match
                best_match = None
                best_score = 0
                for c in candidates:
                    full_name = f"{c.firstName} {c.lastName} {c.shortName}".lower()
                    score = sum(1 for part in name_parts if part.lower() in full_name)
                    if score > best_score:
                        best_score = score
                        best_match = c
                player = best_match
            
            if player:
                wyId = player.wyId
            else:
                return {"response": f"Nu am putut găsi niciun jucător cu numele '{req.playerName}' în baza de date."}
                
        if not wyId:
            return {"response": "Te rog specifică un ID sau un nume de jucător valid."}
            
        response_text = generate_scouting_report(wyId, req.query, db)
        return {"response": response_text}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Mount the frontend static files
app.mount("/", StaticFiles(directory="main-frontend", html=True), name="frontend")
