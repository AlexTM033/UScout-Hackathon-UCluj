"""
NLP Scout Engine — Conversational AI Scout & Twin Player Matchmaker
Dual pipeline: Twin Search (find similar players) + Criteria Search (natural language)
"""
import json
import math
import re
from sqlalchemy.orm import Session
from database import Player, PlayerStats

# ═══════════════════════════════════════════════════════════════
# STEP 1: NLP QUERY PARSER
# ═══════════════════════════════════════════════════════════════

POSITION_MAP = {
    "goalkeeper": ["gk"], "gk": ["gk"],
    "center back": ["cb"], "centre back": ["cb"], "cb": ["cb"], "fundas central": ["cb"],
    "left back": ["lb"], "lb": ["lb"], "full back": ["lb", "rb"], "fullback": ["lb", "rb"],
    "right back": ["rb"], "rb": ["rb"],
    "defensive midfielder": ["cdm"], "cdm": ["cdm"], "dm": ["cdm"],
    "central midfielder": ["cm"], "cm": ["cm"], "midfielder": ["cm", "cdm", "cam"],
    "attacking midfielder": ["cam"], "cam": ["cam"], "playmaker": ["cam", "cm"],
    "left winger": ["lw"], "lw": ["lw"], "left wing": ["lw"],
    "right winger": ["rw"], "rw": ["rw"], "right wing": ["rw"],
    "winger": ["lw", "rw"], "extrema": ["lw", "rw"],
    "striker": ["st"], "forward": ["st"], "st": ["st"], "attacker": ["st", "lw", "rw", "cam"],
    "atacant": ["st"], "fundas": ["cb", "lb", "rb"], "mijlocas": ["cm", "cdm", "cam"],
}

TWIN_KEYWORDS = ["similar", "twin", "like", "asemanator", "inlocui", "replacement", "ca si", "gen ca"]

def parse_query(raw_query: str):
    q = raw_query.lower().strip()
    result = {
        "mode": "criteria",
        "reference_name": None,
        "positions": [],
        "age_max": None,
        "age_min": None,
        "foot": None,
        "min_shooting": None,
        "min_passing": None,
        "min_dribbling": None,
        "min_defending": None,
        "min_physicality": None,
        "min_mentality": None,
        "raw_query": raw_query,
    }

    # Detect TWIN mode
    for kw in TWIN_KEYWORDS:
        if kw in q:
            result["mode"] = "twin"
            # Extract the player name after the keyword
            idx = q.index(kw) + len(kw)
            name_part = q[idx:].strip().strip("\"'").strip()
            # Clean common filler words
            for filler in ["to ", "him ", "pe ", "lui ", "cu ", "a ", "un "]:
                if name_part.startswith(filler):
                    name_part = name_part[len(filler):]
            if name_part:
                result["reference_name"] = name_part.strip()
            break

    # If no twin keyword but query looks like just a player name (2-3 words, no other keywords)
    words = q.split()
    if result["mode"] == "criteria" and 1 <= len(words) <= 4:
        has_pos = any(w in POSITION_MAP for w in words)
        has_age = any(w in ["young", "u21", "tanar", "veteran"] for w in words)
        if not has_pos and not has_age:
            # Might be a direct name search — try twin mode
            result["mode"] = "twin"
            result["reference_name"] = raw_query.strip()

    # Age parsing
    if "u21" in q:
        result["age_max"] = 21
    elif "u23" in q:
        result["age_max"] = 23
    elif "young" in q or "tanar" in q or "tânăr" in q or "tineri" in q:
        result["age_max"] = 23
    elif "veteran" in q or "experienced" in q or "experimentat" in q:
        result["age_min"] = 28

    age_match = re.search(r'(?:age|varsta|vârstă)\s*[<≤]\s*(\d+)', q)
    if age_match:
        result["age_max"] = int(age_match.group(1))
    age_match2 = re.search(r'sub\s+(\d+)\s+ani', q)
    if age_match2:
        result["age_max"] = int(age_match2.group(1))

    # Position parsing
    for key, codes in POSITION_MAP.items():
        if key in q:
            for c in codes:
                if c not in result["positions"]:
                    result["positions"].append(c)

    # Foot parsing
    if "left-footed" in q or "left foot" in q or "stang" in q or "stâng" in q:
        result["foot"] = "left"
    elif "right-footed" in q or "right foot" in q or "drept" in q:
        result["foot"] = "right"

    # Stat threshold parsing
    if "attacking" in q or "ofensiv" in q or "shooter" in q or "finalizare" in q:
        result["min_shooting"] = 60
        result["min_dribbling"] = 60
    if "creative" in q or "creativ" in q or "pase" in q or "pasator" in q:
        result["min_passing"] = 65
    if "dribler" in q or "dribling" in q or "dribbling" in q or "tehnic" in q:
        result["min_dribbling"] = 65
    if "defensive" in q or "defensiv" in q or "intercepti" in q or "interception" in q:
        result["min_defending"] = 65
    if "physical" in q or "fizic" in q or "strong" in q or "puternic" in q:
        result["min_physicality"] = 65
    if "progression" in q or "progresie" in q or "drive" in q:
        result["min_dribbling"] = 65

    return result


# ═══════════════════════════════════════════════════════════════
# STEP 2: DATA LOADING HELPER
# ═══════════════════════════════════════════════════════════════

def _load_all_players_with_radar(db: Session):
    """Load all players with their radar scores from normalized_stats."""
    rows = db.query(Player, PlayerStats).outerjoin(
        PlayerStats, Player.wyId == PlayerStats.wyId
    ).filter(PlayerStats.performance_score != None).all()

    players = []
    for player, stats in rows:
        radar = {}
        bio = {}
        if stats and stats.normalized_stats:
            try:
                ns = json.loads(stats.normalized_stats)
                radar = ns.get("radarScores", {})
            except:
                pass

        # Get CSV bio data
        from csv_lookup import player_match_optimizer
        csv_data = player_match_optimizer(player.firstName or '', player.lastName or '')

        age = None
        if player.birthDate:
            try:
                from datetime import datetime
                bd = datetime.strptime(player.birthDate, "%Y-%m-%d")
                age = (datetime.now() - bd).days // 365
            except:
                pass

        players.append({
            "wyId": player.wyId,
            "name": f"{player.firstName} {player.lastName}".strip() or player.shortName or "Unknown",
            "shortName": player.shortName or "",
            "position": (player.positionCode or "").lower(),
            "age": age,
            "height_cm": csv_data.get("height_cm"),
            "foot": csv_data.get("foot", ""),
            "club": csv_data.get("tm_club", ""),
            "image_url": csv_data.get("image_url"),
            "market_value": csv_data.get("market_value_raw"),
            "performance_score": stats.performance_score if stats else 0,
            "radar": radar,  # { Shooting: 65, Passing: 70, ... }
        })
    return players


# ═══════════════════════════════════════════════════════════════
# STEP 3: SIMILARITY MATCHING (TWIN SEARCH)
# ═══════════════════════════════════════════════════════════════

RADAR_KEYS = ["Shooting", "Passing", "Dribbling", "Defending", "Physicality", "Mentality"]

def _calc_similarity(ref, cand):
    """Calculate weighted similarity between reference and candidate (0-100)."""
    score = 0.0
    total_weight = 0.0

    # Radar similarity (weight: 70%)
    radar_weight = 70.0
    radar_diffs = []
    for key in RADAR_KEYS:
        rv = ref["radar"].get(key, 65)
        cv = cand["radar"].get(key, 65)
        diff = abs(rv - cv)
        # Max possible diff on 40-90 scale = 50
        radar_diffs.append(diff)

    if radar_diffs:
        avg_diff = sum(radar_diffs) / len(radar_diffs)
        # 0 diff = 100%, 25 diff = 50%, 50 diff = 0%
        radar_sim = max(0, 100 - (avg_diff * 2))
        score += radar_sim * (radar_weight / 100)
        total_weight += radar_weight

    # Position similarity (weight: 20%)
    pos_weight = 20.0
    ref_pos = ref["position"]
    cand_pos = cand["position"]
    if ref_pos == cand_pos:
        pos_sim = 100
    elif _positions_related(ref_pos, cand_pos):
        pos_sim = 70
    else:
        pos_sim = 30
    score += pos_sim * (pos_weight / 100)
    total_weight += pos_weight

    # Bio similarity (weight: 10%) — age + height
    bio_weight = 10.0
    bio_sim = 100
    if ref.get("age") and cand.get("age"):
        age_diff = abs(ref["age"] - cand["age"])
        bio_sim -= min(age_diff * 5, 40)
    if ref.get("height_cm") and cand.get("height_cm"):
        try:
            h_diff = abs(float(ref["height_cm"]) - float(cand["height_cm"]))
            bio_sim -= min(h_diff * 2, 20)
        except:
            pass
    score += max(0, bio_sim) * (bio_weight / 100)
    total_weight += bio_weight

    raw = score if total_weight > 0 else 50
    # Clamp to 70-95 range for recommended matches
    return round(max(0, min(99, raw)), 1)


def _positions_related(p1, p2):
    groups = [
        {"gk"},
        {"cb", "lb", "rb"},
        {"cdm", "cm", "cam"},
        {"lw", "rw", "lm", "rm"},
        {"st"},
    ]
    for g in groups:
        if p1 in g and p2 in g:
            return True
    return False


def find_twin_matches(reference_name: str, db: Session, parsed):
    """Find top 3 similar players to a reference player."""
    all_players = _load_all_players_with_radar(db)

    # Find the reference player by name
    ref = None
    ref_name_lower = reference_name.lower()
    for p in all_players:
        if ref_name_lower in p["name"].lower() or ref_name_lower in p["shortName"].lower():
            ref = p
            break

    if not ref:
        # Fuzzy fallback: check if any word matches
        words = ref_name_lower.split()
        best = None
        best_score = 0
        for p in all_players:
            pname = p["name"].lower() + " " + p["shortName"].lower()
            sc = sum(1 for w in words if w in pname)
            if sc > best_score:
                best_score = sc
                best = p
        ref = best

    if not ref:
        return None, "Nu am găsit jucătorul de referință în baza de date."

    # Calculate similarity for all other players
    candidates = []
    for p in all_players:
        if p["wyId"] == ref["wyId"]:
            continue

        # Apply optional filters from parsed query
        if parsed.get("age_max") and p.get("age") and p["age"] > parsed["age_max"]:
            continue
        if parsed.get("age_min") and p.get("age") and p["age"] < parsed["age_min"]:
            continue

        sim = _calc_similarity(ref, p)
        if sim >= 50:  # Only recommend decent matches
            candidates.append({**p, "matchPercentage": sim})

    candidates.sort(key=lambda x: x["matchPercentage"], reverse=True)
    top3 = candidates[:3]

    # Build response
    ref_display = f"{ref['name']} ({ref['position'].upper()}, {ref.get('age', '?')} ani)"
    summary = f"Am identificat cele mai similare profile cu {ref_display} din baza de date, pe baza analizei celor 6 axe de performanță (scara 40-90) și a datelor biografice."

    recommendations = []
    for c in top3:
        # Generate AI summary
        strengths = []
        weaknesses = []
        for key in RADAR_KEYS:
            rv = ref["radar"].get(key, 65)
            cv = c["radar"].get(key, 65)
            diff = cv - rv
            if diff >= 5:
                strengths.append(f"{key} superior (+{diff:.0f})")
            elif diff <= -5:
                weaknesses.append(f"{key} inferior ({diff:.0f})")

        ai_parts = [f"Potrivire {c['matchPercentage']}% cu {ref['name']}."]
        if strengths:
            ai_parts.append(f"Puncte forte: {', '.join(strengths[:2])}.")
        if weaknesses:
            ai_parts.append(f"De îmbunătățit: {', '.join(weaknesses[:2])}.")

        recommendations.append({
            "playerId": c["wyId"],
            "name": c["name"],
            "matchPercentage": round(c["matchPercentage"]),
            "primaryPosition": c["position"].upper(),
            "dynamicOverallScore": round(c["performance_score"]),
            "csvMetaData": {
                "age": c.get("age"),
                "preferredFoot": c.get("foot", "N/A"),
                "height": c.get("height_cm"),
                "club": c.get("club", "N/A"),
                "marketValue": c.get("market_value"),
                "imageUrl": c.get("image_url"),
            },
            "radarScores": c.get("radar", {}),
            "aiSummary": " ".join(ai_parts),
        })

    return {
        "scoutingSummary": summary,
        "referencePlayer": {
            "name": ref["name"],
            "position": ref["position"].upper(),
            "age": ref.get("age"),
            "wyId": ref["wyId"],
        },
        "recommendations": recommendations,
    }, None


# ═══════════════════════════════════════════════════════════════
# STEP 4: CRITERIA-BASED SEARCH
# ═══════════════════════════════════════════════════════════════

def find_criteria_matches(parsed, db: Session):
    """Find top 3 players matching natural language criteria."""
    all_players = _load_all_players_with_radar(db)

    candidates = []
    for p in all_players:
        # Position filter
        if parsed["positions"]:
            if p["position"] not in parsed["positions"]:
                continue

        # Age filters
        if parsed["age_max"] and p.get("age") and p["age"] > parsed["age_max"]:
            continue
        if parsed["age_min"] and p.get("age") and p["age"] < parsed["age_min"]:
            continue

        # Foot filter
        if parsed["foot"]:
            pfoot = (p.get("foot") or "").lower()
            if parsed["foot"] == "left" and "left" not in pfoot and "stâng" not in pfoot:
                continue
            if parsed["foot"] == "right" and "right" not in pfoot and "drept" not in pfoot:
                continue

        # Radar score filters
        radar = p.get("radar", {})
        if parsed["min_shooting"] and radar.get("Shooting", 0) < parsed["min_shooting"]:
            continue
        if parsed["min_passing"] and radar.get("Passing", 0) < parsed["min_passing"]:
            continue
        if parsed["min_dribbling"] and radar.get("Dribbling", 0) < parsed["min_dribbling"]:
            continue
        if parsed["min_defending"] and radar.get("Defending", 0) < parsed["min_defending"]:
            continue
        if parsed["min_physicality"] and radar.get("Physicality", 0) < parsed["min_physicality"]:
            continue
        if parsed["min_mentality"] and radar.get("Mentality", 0) < parsed["min_mentality"]:
            continue

        # Calculate a "fit score" — how well they match the desired profile
        fit = _calc_criteria_fit(p, parsed)
        candidates.append({**p, "matchPercentage": fit})

    candidates.sort(key=lambda x: x["matchPercentage"], reverse=True)
    top3 = candidates[:3]

    # Build summary
    criteria_parts = []
    if parsed["positions"]:
        criteria_parts.append(f"Poziție: {', '.join(p.upper() for p in parsed['positions'])}")
    if parsed["age_max"]:
        criteria_parts.append(f"Vârstă ≤ {parsed['age_max']}")
    if parsed["foot"]:
        criteria_parts.append(f"Picior: {parsed['foot']}")

    summary = f"Am analizat baza de date și am identificat cele mai bune potriviri pentru criteriile: {'; '.join(criteria_parts) if criteria_parts else parsed['raw_query']}."

    recommendations = []
    for c in top3:
        radar = c.get("radar", {})
        top_stats = sorted(radar.items(), key=lambda x: x[1], reverse=True)[:2]
        stat_desc = ", ".join(f"{k}: {v}" for k, v in top_stats)

        recommendations.append({
            "playerId": c["wyId"],
            "name": c["name"],
            "matchPercentage": round(c["matchPercentage"]),
            "primaryPosition": c["position"].upper(),
            "dynamicOverallScore": round(c["performance_score"]),
            "csvMetaData": {
                "age": c.get("age"),
                "preferredFoot": c.get("foot", "N/A"),
                "height": c.get("height_cm"),
                "club": c.get("club", "N/A"),
                "marketValue": c.get("market_value"),
                "imageUrl": c.get("image_url"),
            },
            "radarScores": c.get("radar", {}),
            "aiSummary": f"Scor dinamic: {round(c['performance_score'])}. Cele mai puternice axe: {stat_desc}.",
        })

    return {
        "scoutingSummary": summary,
        "referencePlayer": None,
        "recommendations": recommendations,
    }, None


def _calc_criteria_fit(player, parsed):
    """Score how well a player fits the parsed criteria (0-95)."""
    score = 50.0  # Base

    # Position match bonus
    if parsed["positions"] and player["position"] in parsed["positions"]:
        score += 10

    # Performance score contribution (normalized to 0-20 range)
    perf = player.get("performance_score", 50)
    score += min((perf - 40) * 0.4, 20)

    # Radar bonuses for requested skills
    radar = player.get("radar", {})
    bonus_count = 0
    for field, key in [
        ("min_shooting", "Shooting"), ("min_passing", "Passing"),
        ("min_dribbling", "Dribbling"), ("min_defending", "Defending"),
        ("min_physicality", "Physicality"), ("min_mentality", "Mentality"),
    ]:
        threshold = parsed.get(field)
        if threshold:
            val = radar.get(key, 50)
            if val >= threshold:
                score += 5
                bonus_count += 1

    # Age preference bonus
    if parsed["age_max"] and player.get("age"):
        if player["age"] <= parsed["age_max"]:
            youth_bonus = max(0, (parsed["age_max"] - player["age"]) * 1.5)
            score += min(youth_bonus, 8)

    return round(max(70, min(95, score)), 1)


# ═══════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════

def ai_scout_search(raw_query: str, db: Session):
    """Main entry: parse query, route to twin or criteria pipeline, return structured JSON."""
    parsed = parse_query(raw_query)

    if parsed["mode"] == "twin" and parsed["reference_name"]:
        result, error = find_twin_matches(parsed["reference_name"], db, parsed)
    else:
        result, error = find_criteria_matches(parsed, db)

    if error:
        return {"aiResponse": {"scoutingSummary": error, "recommendations": []}}

    return {"aiResponse": result}
