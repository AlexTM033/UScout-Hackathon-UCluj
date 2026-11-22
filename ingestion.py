import os
import json
import re
import pandas as pd
from typing import List, Dict, Tuple, Set
from collections import defaultdict
from sqlalchemy.orm import Session
from database import Player, PlayerStats
from scoring import calculate_all_category_scores, map_archetype_from_name
from analysis import generate_scouting_analysis
from csv_lookup import get_height_index

DATA_DIR = "./Date - meciuri"
PLAYERS_FILE = "players (1).json"

# STEP 1: THE STANDARD 12-POSITION MAPPING DICTIONARY
MASTER_POSITIONS = {
    "GK": {"name": "Goalkeeper", "matches": ["gk", "gkp"]},
    "CB": {"name": "Center Back", "matches": ["cb", "lcb", "rcb", "sw"]},
    "LB": {"name": "Left Back", "matches": ["lb", "lwb"]},
    "RB": {"name": "Right Back", "matches": ["rb", "rwb"]},
    "CDM": {"name": "Central Defensive Midfielder", "matches": ["dm", "ldm", "rdm", "cdm"]},
    "CM": {"name": "Central Midfielder", "matches": ["cm", "lcm", "rcm", "lcmf", "rcmf"]},
    "CAM": {"name": "Central Attacking Midfielder", "matches": ["am", "lam", "ram", "cam"]},
    "LM": {"name": "Left Midfielder", "matches": ["lm", "lmf"]},
    "RM": {"name": "Right Midfielder", "matches": ["rm", "rmf"]},
    "LW": {"name": "Left Winger", "matches": ["lw", "lwf"]},
    "RW": {"name": "Right Winger", "matches": ["rw", "rwf"]},
    "ST": {"name": "Striker", "matches": ["st", "cf", "lf", "rf", "ss", "fw"]}
}

# STEP 3: STRICT GLOBAL UI ORDERING
POSITION_ORDER = ["GK", "CB", "LB", "RB", "CDM", "CM", "CAM", "LM", "RM", "LW", "RW", "ST"]

_global_advanced_metrics_df = None
_global_discovered_positions = []
_global_search_index = {}

SIGNIFICANCE_THRESHOLD = 10  # Position must account for 10% of playtime to be included
MAX_SECONDARY = 2           # Max secondary positions to show

def get_global_discovered_positions():
    return _global_discovered_positions

def get_global_search_index():
    return _global_search_index

def load_advanced_metrics():
    global _global_advanced_metrics_df
    if os.path.exists("processed_metrics.pkl"):
        try:
            _global_advanced_metrics_df = pd.read_pickle("processed_metrics.pkl")
            print(f"Loaded {len(_global_advanced_metrics_df)} players into advanced metrics cache.")
        except Exception as e:
            print(f"Error loading advanced metrics: {e}")

def normalize_position(raw_code):
    """Maps messy position codes to Master Positions."""
    code = str(raw_code).lower()
    for master, data in MASTER_POSITIONS.items():
        if any(m in code for m in data["matches"]):
            return master
    return None

def process_players_file() -> List[Dict]:
    file_path = os.path.join(DATA_DIR, PLAYERS_FILE)
    if not os.path.exists(file_path):
        return []
        
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    players = []
    for p in data.get("players", []):
        role = p.get("role", {})
        players.append({
            "wyId": p.get("wyId"),
            "shortName": p.get("shortName"),
            "firstName": p.get("firstName"),
            "lastName": p.get("lastName"),
            "birthDate": p.get("birthDate"),
            "positionCode": role.get("code3", "").lower(),
            "fallbackRoleName": role.get("name", "")  # e.g., "Midfielder", "Defender"
        })
    return players

def build_position_ledger(data_dir: str) -> Tuple[Dict, List[Dict]]:
    """
    STEP 1: Scan ALL match files and build a Position Ledger for every player.
    Tracks exact minutes in each specific position (code + name) across the season.
    Also discovers all unique positions globally.
    
    Returns:
        ledger: {playerId: {code: {"name": str, "minutes": float}}}
        discovered_positions: [{"name": str, "code": str}]
    """
    # ledger[playerId][code] = {"name": "...", "minutes": float}
    ledger = defaultdict(lambda: defaultdict(lambda: {"name": "", "minutes": 0.0}))
    
    # Track all unique positions: {code: name}
    unique_positions = {}
    
    for filename in os.listdir(data_dir):
        if not filename.endswith("players_stats.json"):
            continue
            
        file_path = os.path.join(data_dir, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for player in data.get("players", []):
                player_id = player.get("playerId")
                total_minutes = player.get("total", {}).get("minutesOnField", 0)
                positions = player.get("positions", [])
                
                if total_minutes <= 0 or not positions:
                    continue
                    
                for pos_entry in positions:
                    pos_obj = pos_entry.get("position", {})
                    raw_code = pos_obj.get("code", "").strip()
                    pos_name = pos_obj.get("name", "").strip()
                    percent = pos_entry.get("percent", 0)
                    
                    if not raw_code or percent <= 0:
                        continue
                    
                    # GLOBAL TRACKING: Register every unique position found
                    if raw_code not in unique_positions:
                        unique_positions[raw_code] = pos_name
                    
                    role_minutes = total_minutes * (percent / 100.0)
                    ledger[player_id][raw_code]["name"] = pos_name
                    ledger[player_id][raw_code]["minutes"] += role_minutes
                        
        except Exception as e:
            print(f"Error processing {filename} for position ledger: {e}")
    
    # Build the sorted discovered positions list
    discovered = sorted(
        [{"name": name, "code": code} for code, name in unique_positions.items()],
        key=lambda x: x["name"]
    )
    
    return ledger, discovered

def determine_positions(ledger_entry: Dict) -> Dict:
    """
    Position Normalization & Merging Engine:
    1. Map raw codes to Master Positions
    2. Merge duplicate roles (sum minutes)
    3. Calculate primary and secondary (Rule of Three)
    """
    if not ledger_entry:
        return {"primary": None, "secondary": [], "absoluteTotalMinutes": 0}
    
    # STEP 1 & 2: Map and Merge Duplicates
    merged_ledger = defaultdict(lambda: {"name": "", "minutes": 0})
    for raw_code, data in ledger_entry.items():
        master_code = normalize_position(raw_code)
        if master_code:
            merged_ledger[master_code]["name"] = MASTER_POSITIONS[master_code]["name"]
            merged_ledger[master_code]["minutes"] += data["minutes"]
    
    if not merged_ledger:
        return {"primary": None, "secondary": [], "absoluteTotalMinutes": 0}
    
    # Calculate absolute total minutes
    absolute_total = sum(entry["minutes"] for entry in merged_ledger.values())
    
    # STEP 2b: Recalculate Primary/Secondary
    significant_positions = []
    for code, data in merged_ledger.items():
        weight = (data["minutes"] / absolute_total) * 100
        if weight >= SIGNIFICANCE_THRESHOLD:
            significant_positions.append({
                "code": code,
                "name": data["name"],
                "minutes": round(data["minutes"]),
                "percentageOfPlaytime": round(weight, 1)
            })
    
    # Sort by minutes descending
    significant_positions.sort(key=lambda x: x["minutes"], reverse=True)
    
    # If threshold filtered everything, keep at least the top position
    if not significant_positions:
        top_code = max(merged_ledger.keys(), key=lambda k: merged_ledger[k]["minutes"])
        top_data = merged_ledger[top_code]
        weight = (top_data["minutes"] / absolute_total) * 100
        significant_positions = [{
            "code": top_code,
            "name": top_data["name"],
            "minutes": round(top_data["minutes"]),
            "percentageOfPlaytime": round(weight, 1)
        }]
    
    primary = significant_positions[0]
    secondary = significant_positions[1:1 + MAX_SECONDARY]
    
    return {
        "primary": primary,
        "secondary": secondary,
        "absoluteTotalMinutes": round(absolute_total)
    }

def process_match_files() -> List[Dict]:
    all_player_stats = []
    
    for filename in os.listdir(DATA_DIR):
        if not filename.endswith("players_stats.json"):
            continue
            
        file_path = os.path.join(DATA_DIR, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for player in data.get("players", []):
                playerId = player.get("playerId")
                
                total_stats = player.get("total", {})
                percent_stats = player.get("percent", {})
                
                stat_entry = {"wyId": playerId}
                
                for k, v in total_stats.items():
                    stat_entry[f"total_{k}"] = v
                for k, v in percent_stats.items():
                    stat_entry[f"percent_{k}"] = v
                    
                all_player_stats.append(stat_entry)
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            
    return all_player_stats

# Fallback mapping for players with zero match data
FALLBACK_ROLE_MAP = {
    "Defender": "CB",
    "Midfielder": "CM / DM",
    "Forward": "ST / CF",
    "Goalkeeper": "GK"
}

def run_ingestion(db: Session):
    global _global_discovered_positions, _global_search_index
    
    print("Ingesting master players list...")
    master_players = process_players_file()
    
    fallback_roles = {}
    for p in master_players:
        fallback_roles[p["wyId"]] = p.get("fallbackRoleName", "")
        existing = db.query(Player).filter(Player.wyId == p["wyId"]).first()
        if not existing:
            new_player = Player(
                wyId=p["wyId"],
                shortName=p["shortName"],
                firstName=p["firstName"],
                lastName=p["lastName"],
                birthDate=p["birthDate"],
                positionCode=p["positionCode"]
            )
            db.add(new_player)
    db.commit()
    
    # STEP 1: Build Position Ledger & Discover All Positions
    print("Building Position Ledger from match data...")
    position_ledger, discovered_positions = build_position_ledger(DATA_DIR)
    _global_discovered_positions = discovered_positions
    print(f"  Position data tracked for {len(position_ledger)} players.")
    print(f"  Discovered {len(discovered_positions)} unique positions globally.")
    
    print("Ingesting match stats...")
    match_stats = process_match_files()
    
    if not match_stats:
        print("No match stats found.")
        return
        
    df = pd.DataFrame(match_stats)
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    if 'wyId' in numeric_cols:
        numeric_cols.remove('wyId')
    
    agg_dict = {}
    for col in numeric_cols:
        if col.startswith('percent_'):
            agg_dict[col] = 'mean'
        else:
            agg_dict[col] = 'sum'
            
    grouped = df.groupby('wyId').agg(agg_dict).reset_index()
    
    if 'total_minutesOnField' in grouped.columns:
        grouped = grouped[grouped['total_minutesOnField'] >= 450]
    
    print(f"Processing {len(grouped)} players with >= 450 minutes...")
    
    # MODULE 2: DATA INGESTION & MATH ENGINE
    master_positions_dict = {}
    for wyId, ledger in position_ledger.items():
        calculated = determine_positions(ledger)
        if calculated["primary"]:
            master_positions_dict[wyId] = calculated["primary"]["code"]
        else:
            fb_role = fallback_roles.get(wyId, "Midfielder")
            master_positions_dict[wyId] = FALLBACK_ROLE_MAP.get(fb_role, "CM / DM").split(" ")[0].upper()
            
    from math_engine import run_pandas_pipeline
    grouped = run_pandas_pipeline(grouped, master_positions_dict)
    
    # Save the dataframe globally for the AI Engine RAG
    global _global_advanced_metrics_df
    _global_advanced_metrics_df = grouped
    
    # Persist to disk so tactical fit works after restart
    try:
        grouped.to_pickle("processed_metrics.pkl")
        print("Advanced metrics persisted to processed_metrics.pkl")
    except Exception as e:
        print(f"Warning: Could not persist metrics: {e}")
    
    search_index = defaultdict(list)
    
    # Pre-calculate normalized stats for ALL players to enable batch population scoring
    all_players_data = []
    player_id_to_norm_stats = {}
    player_id_to_archetype = {}
    player_id_to_positions = {}
    
    for _, row in grouped.iterrows():
        wyId = int(row['wyId'])
        minutes = row.get('total_minutesOnField', 0)
        
        normalized_stats = {}
        for col in numeric_cols:
            val = row[col]
            if col.startswith('total_') and col != 'total_minutesOnField':
                p90_val = (val / minutes) * 90 if minutes > 0 else 0
                normalized_stats[col.replace('total_', '')] = round(p90_val, 2)
            elif col.startswith('percent_'):
                normalized_stats[col.replace('percent_', 'percent.')] = round(val, 2)
            else:
                normalized_stats[col] = round(val, 2)
        
        normalized_stats["minutesOnField"] = minutes
        normalized_stats["yellowCards"] = row.get('total_yellowCards', 0)
        normalized_stats["directRedCards"] = row.get('total_directRedCards', 0)
        normalized_stats["dangerousOwnHalfLosses"] = row.get('total_dangerousOwnHalfLosses', 0)
        
        # Determine archetype
        player_ledger = position_ledger.get(wyId, {})
        calculated_roles = determine_positions(player_ledger)
        
        if calculated_roles["primary"]:
            archetype = map_archetype_from_name(calculated_roles["primary"]["name"])
            primary_code = calculated_roles["primary"]["code"]
        else:
            fb_role = fallback_roles.get(wyId, "Midfielder")
            archetype = FALLBACK_ROLE_MAP.get(fb_role, "CM / DM")
            primary_code = "cm"
            calculated_roles["primary"] = {"name": fb_role, "code": primary_code, "minutes": 0, "percentageOfPlaytime": 0}

        # Store for batch scoring
        player_obj = db.query(Player).filter(Player.wyId == wyId).first()
        all_players_data.append({
            "wyId": wyId,
            "archetype": archetype,
            "normalized_stats": normalized_stats,
            "firstName": player_obj.firstName if player_obj else "",
            "lastName": player_obj.lastName if player_obj else ""
        })
        
        player_id_to_norm_stats[wyId] = normalized_stats
        player_id_to_archetype[wyId] = archetype
        player_id_to_positions[wyId] = calculated_roles

    # BATCH SCORING (PHASE 3+4)
    print(f"Calculating population-based scores for {len(all_players_data)} players...")
    height_index = get_height_index()
    batch_scores = calculate_all_category_scores(all_players_data, height_index)
    
    # Save to DB
    for wyId, score_data in batch_scores.items():
        norm_stats = player_id_to_norm_stats[wyId]
        archetype = player_id_to_archetype[wyId]
        roles = player_id_to_positions[wyId]
        
        # Generate Scouting Insights
        analysis_data = generate_scouting_analysis(wyId, roles["primary"]["code"], norm_stats)
        
        final_ui_stats = {
            "playerId": wyId,
            "evaluatedPosition": archetype,
            "radarScores": score_data.get('radarScores', {}),
            "scoutingAnalysis": analysis_data.get('scoutingAnalysis', {"pros": [], "cons": []}),
            "topTraits": score_data.get('topTraits', []),
            "liabilityWarning": score_data.get('liabilityWarning'),
            "minutesOnField": norm_stats["minutesOnField"],
            "tacticalProfile": {
                "primaryPosition": roles["primary"],
                "mappedArchetype": archetype,
                "absoluteTotalMinutes": roles["absoluteTotalMinutes"],
                "secondaryPositions": roles["secondary"]
            }
        }
        
        # Update search index
        playable_positions = [roles["primary"]] + roles["secondary"]
        for pos in playable_positions:
            if pos: search_index[pos["code"].lower()].append(wyId)
        
        # Update Player position
        player = db.query(Player).filter(Player.wyId == wyId).first()
        if player: player.positionCode = roles["primary"]["code"]
        
        # Update Stats record
        stats_record = db.query(PlayerStats).filter(PlayerStats.wyId == wyId).first()
        score = score_data['overallRating']
        
        if stats_record:
            stats_record.minutesOnField = norm_stats["minutesOnField"]
            stats_record.performance_score = float(score)
            stats_record.normalized_stats = json.dumps(final_ui_stats)
        else:
            new_stats = PlayerStats(
                wyId=wyId,
                minutesOnField=norm_stats["minutesOnField"],
                performance_score=float(score),
                normalized_stats=json.dumps(final_ui_stats)
            )
            db.add(new_stats)
            
    _global_search_index = dict(search_index)
    print(f"  Search index built with {len(_global_search_index)} position groups.")
    
    db.commit()
    print("Ingestion complete.")
