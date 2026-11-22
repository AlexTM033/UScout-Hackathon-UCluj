"""
Deep Metric Scoring Engine v3 — Bayesian Smoothing + Strict 40-90 Clamping

Pipeline:
  1. Confidence Weighting (regression to mean for low-minute players)
  2. Population Z-score per category
  3. Z → 40-90 mapping: score = 65 + (Z * 8), hard-clamped [40, 90]
  4. Overall = weighted average of clamped category scores (guaranteed 40-90)
"""
import numpy as np
from typing import Dict, List, Any, Optional
import math


# ═══════════════════════════════════════════════════════════════════════
# STEP 1: CONFIDENCE WEIGHTING CONSTANTS
# ═══════════════════════════════════════════════════════════════════════

BASELINE_MINUTES = 270  # 3 full games — minimum for full confidence


# ═══════════════════════════════════════════════════════════════════════
# DEEP METRIC CATEGORY DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════
# (stat_key, weight, is_inverted)

OUTFIELD_CATEGORIES = {
    "Shooting": [
        ("xgShot", 2.0, False),
        ("goals", 2.0, False),
        ("shots", 1.0, False),
        ("percent.shotsOnTarget", 1.5, False),
        ("percent.goalConversion", 1.5, False),
        ("percent.headShotsOnTarget", 0.5, False),
        ("touchInBox", 1.5, False),
    ],
    "Passing": [
        ("assists", 1.5, False),
        ("xgAssist", 1.5, False),
        ("secondAssists", 0.8, False),
        ("thirdAssists", 0.5, False),
        ("keyPasses", 1.5, False),
        ("smartPasses", 1.5, False),
        ("progressivePasses", 1.5, False),
        ("percent.successfulPassesToFinalThird", 1.0, False),
        ("percent.successfulThroughPasses", 0.8, False),
        ("percent.successfulCrosses", 0.8, False),
    ],
    "Dribbling": [
        ("progressiveRun", 2.0, False),
        ("accelerations", 1.5, False),
        ("percent.successfulDribbles", 2.0, False),
        ("percent.offensiveDuelsWon", 1.5, False),
        ("foulsSuffered", 1.0, False),
        ("percent.successfulAttackingActions", 1.5, False),
    ],
    "Defending": [
        ("interceptions", 1.5, False),
        ("clearances", 1.0, False),
        ("slidingTackles", 0.8, False),
        ("recoveries", 1.0, False),
        ("dangerousOpponentHalfRecoveries", 1.5, False),
        ("counterpressingRecoveries", 1.5, False),
        ("percent.defensiveDuelsWon", 2.0, False),
        ("percent.dribblesAgainstWon", 1.5, False),
        ("percent.successfulDefensiveAction", 1.5, False),
    ],
    "Physicality": [
        ("percent.aerialDuelsWon", 2.0, False),
        ("percent.fieldAerialDuelsWon", 1.5, False),
        ("pressingDuels", 1.5, False),
        ("percent.looseBallDuelsWon", 1.5, False),
        ("percent.duelsWon", 1.5, False),
    ],
    "Mentality": [
        ("percent.successfulLinkupPlays", 1.5, False),
        ("percent.successfulBackPasses", 1.0, False),
        ("dangerousOwnHalfLosses", 2.0, True),
        ("losses", 1.5, True),
        ("offsides", 0.5, True),
        ("yellowCards", 1.0, True),
        ("directRedCards", 2.0, True),
        ("percent.yellowCardsPerFoul", 1.0, True),
    ],
}

GK_CATEGORIES = {
    "Saving": [
        ("percent.gkSaves", 2.5, False),
        ("xgSave", 2.0, False),
        ("gkShotsAgainst", 1.0, False),
    ],
    "Distribution": [
        ("percent.successfulPasses", 2.0, False),
        ("percent.successfulLongPasses", 1.5, False),
        ("goalKicksShort", 1.0, False),
    ],
    "Reflexes": [
        ("percent.gkSaves", 1.5, False),
        ("xgSave", 2.0, False),
        ("gkConcededGoals", 1.5, True),
    ],
    "Positioning": [
        ("percent.gkSuccessfulExits", 2.0, False),
        ("gkAerialDuelsWon", 1.5, False),
    ],
    "Handling": [
        ("gkCleanSheets", 2.0, False),
        ("missedBalls", 1.5, True),
    ],
    "Mentality": [
        ("dangerousOwnHalfLosses", 2.0, True),
        ("yellowCards", 1.0, True),
        ("directRedCards", 2.0, True),
    ],
}


# ═══════════════════════════════════════════════════════════════════════
# POSITION-DYNAMIC WEIGHTS
# ═══════════════════════════════════════════════════════════════════════

POSITION_WEIGHTS_OUTFIELD = {
    "ST / CF": {"Shooting": 0.45, "Passing": 0.15, "Dribbling": 0.20, "Defending": 0.05, "Physicality": 0.15, "Mentality": 0.00},
    "LW / RW": {"Shooting": 0.25, "Passing": 0.25, "Dribbling": 0.30, "Defending": 0.10, "Physicality": 0.10, "Mentality": 0.00},
    "AM":      {"Shooting": 0.10, "Passing": 0.40, "Dribbling": 0.25, "Defending": 0.10, "Physicality": 0.00, "Mentality": 0.15},
    "CM / DM": {"Shooting": 0.10, "Passing": 0.40, "Dribbling": 0.25, "Defending": 0.10, "Physicality": 0.00, "Mentality": 0.15},
    "CDM":     {"Shooting": 0.00, "Passing": 0.25, "Dribbling": 0.00, "Defending": 0.40, "Physicality": 0.20, "Mentality": 0.15},
    "CB":      {"Shooting": 0.00, "Passing": 0.10, "Dribbling": 0.00, "Defending": 0.65, "Physicality": 0.25, "Mentality": 0.00},
    "LB / RB": {"Shooting": 0.00, "Passing": 0.25, "Dribbling": 0.20, "Defending": 0.35, "Physicality": 0.20, "Mentality": 0.00},
}

POSITION_WEIGHTS_GK = {
    "GK": {"Saving": 0.40, "Distribution": 0.10, "Reflexes": 0.15, "Positioning": 0.20, "Handling": 0.15, "Mentality": 0.00},
}


# ═══════════════════════════════════════════════════════════════════════
# ARCHETYPE MAPPER
# ═══════════════════════════════════════════════════════════════════════

def map_archetype_from_name(position_name: str) -> str:
    if not position_name:
        return "CM / DM"
    name = position_name.lower()
    if "goalkeeper" in name:
        return "GK"
    elif "striker" in name or "forward" in name:
        return "ST / CF"
    elif "attacking midfielder" in name:
        return "AM"
    elif "winger" in name or "wide" in name:
        return "LW / RW"
    elif name in ["left midfielder", "right midfielder"]:
        return "LW / RW"
    elif "defensive midfielder" in name:
        return "CDM"
    elif "central midfielder" in name:
        return "CM / DM"
    elif "centre back" in name or "center back" in name or "sweeper" in name:
        return "CB"
    elif "back" in name and "centre" not in name and "center" not in name:
        return "LB / RB"
    elif "midfielder" in name:
        return "CM / DM"
    elif "defender" in name:
        return "CB"
    else:
        return "CM / DM"


# ═══════════════════════════════════════════════════════════════════════
# STEP 2: THE UNBREAKABLE 40-90 CLAMP
# ═══════════════════════════════════════════════════════════════════════

def clamp_40_90(z_score: float) -> int:
    """
    Maps Z-score directly to 40-90 scale.
    Mean (Z=0) = 65, 1 SD = 8 points.
    HARD CLAMPED: output is ALWAYS in [40, 90]. No exceptions.
    """
    raw = 65 + (z_score * 8)
    return int(math.floor(max(40, min(90, raw))))


# ═══════════════════════════════════════════════════════════════════════
# STEP 1: CONFIDENCE-WEIGHTED COMPOSITE CALCULATION
# ═══════════════════════════════════════════════════════════════════════

def _compute_composite_raw(
    stats: Dict,
    category_metrics: List,
    confidence: float,
    league_avg_stats: Dict,
    height_cm: Optional[int] = None,
    is_physicality: bool = False,
) -> float:
    """
    Compute a weighted composite raw score for one player in one category.
    Applies Bayesian regression to mean for low-minute players.
    """
    total_weighted = 0.0
    total_weight = 0.0

    for metric_key, weight, inverted in category_metrics:
        raw_val = stats.get(metric_key, 0.0)
        if raw_val is None:
            raw_val = 0.0

        # STEP 1: Regression to the mean
        league_avg = league_avg_stats.get(metric_key, 0.0)
        adjusted_val = (raw_val * confidence) + (league_avg * (1.0 - confidence))

        if inverted:
            adjusted_val = -adjusted_val

        total_weighted += adjusted_val * weight
        total_weight += weight

    composite = total_weighted / total_weight if total_weight > 0 else 0.0

    # Height modifier for Physicality
    if is_physicality and height_cm and height_cm > 0:
        height_modifier = 1.0 + (height_cm - 180) * 0.005
        height_modifier = max(0.85, min(1.15, height_modifier))
        composite *= height_modifier

    return composite


# ═══════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT: BATCH POPULATION SCORING
# ═══════════════════════════════════════════════════════════════════════

def calculate_all_category_scores(
    all_players: List[Dict],
    height_index: Dict[str, int],
) -> Dict[int, Dict]:
    """
    Process ALL players at once with:
      1. Confidence weighting (regression to mean)
      2. Population Z-scores
      3. Strict 40-90 clamping
      4. Position-dynamic overall rating

    Args:
        all_players: list of dicts with 'wyId', 'archetype', 'normalized_stats',
                     'firstName', 'lastName'
        height_index: normalized_name -> height_cm

    Returns:
        {wyId: {
            'radarScores': {category: int(40-90)},
            'overallRating': int(40-90),
            'topTraits': [str, str],
            'liabilityWarning': str or None
        }}
    """
    if not all_players:
        return {}

    gk_players = [p for p in all_players if p['archetype'] == 'GK']
    outfield_players = [p for p in all_players if p['archetype'] != 'GK']

    results = {}

    if outfield_players:
        results.update(_process_group(outfield_players, OUTFIELD_CATEGORIES, POSITION_WEIGHTS_OUTFIELD, height_index))

    if gk_players:
        results.update(_process_group(gk_players, GK_CATEGORIES, POSITION_WEIGHTS_GK, height_index))

    return results


def _compute_league_averages(players: List[Dict], categories: Dict) -> Dict[str, float]:
    """Compute league-average p90 for every metric across the player group."""
    metric_sums = {}
    metric_counts = {}

    # Gather all unique metric keys
    all_metrics = set()
    for cat_metrics in categories.values():
        for metric_key, _, _ in cat_metrics:
            all_metrics.add(metric_key)

    for metric_key in all_metrics:
        metric_sums[metric_key] = 0.0
        metric_counts[metric_key] = 0

    for player in players:
        stats = player['normalized_stats']
        for metric_key in all_metrics:
            val = stats.get(metric_key, 0.0)
            if val is None:
                val = 0.0
            metric_sums[metric_key] += val
            metric_counts[metric_key] += 1

    averages = {}
    for metric_key in all_metrics:
        count = metric_counts[metric_key]
        averages[metric_key] = metric_sums[metric_key] / count if count > 0 else 0.0

    return averages


def _process_group(
    players: List[Dict],
    categories: Dict,
    weight_tables: Dict,
    height_index: Dict[str, int],
) -> Dict[int, Dict]:
    """Process a group of players through the Bayesian Z-score → 40-90 pipeline."""
    from csv_lookup import _normalize

    results = {}
    category_names = list(categories.keys())

    # STEP 1a: Compute league averages for regression-to-mean
    league_avg_stats = _compute_league_averages(players, categories)

    # STEP 1b: Compute confidence-weighted composites for each player × category
    raw_matrix = {}  # {category: np.array of raw composites}

    for cat_name, metrics in categories.items():
        raw_scores = []
        for player in players:
            stats = player['normalized_stats']
            minutes = stats.get('minutesOnField', 0)

            # Confidence factor
            confidence = min(1.0, minutes / BASELINE_MINUTES) if BASELINE_MINUTES > 0 else 1.0

            # Get height for physicality modifier
            full_name = f"{player.get('firstName', '')} {player.get('lastName', '')}".strip()
            norm_name = _normalize(full_name)
            height = height_index.get(norm_name)

            is_phys = (cat_name == "Physicality")
            raw = _compute_composite_raw(stats, metrics, confidence, league_avg_stats, height, is_phys)
            raw_scores.append(raw)

        raw_matrix[cat_name] = np.array(raw_scores, dtype=float)

    # STEP 2: Z-score each category across population
    z_matrix = {}
    for cat_name, raw_arr in raw_matrix.items():
        std = np.std(raw_arr)
        if std > 0 and len(raw_arr) > 1:
            z_scores = (raw_arr - np.mean(raw_arr)) / std
        else:
            z_scores = np.zeros_like(raw_arr)
        z_matrix[cat_name] = z_scores

    # STEP 2+3: Z → 40-90 clamp, then weighted overall (guaranteed 40-90)
    for i, player in enumerate(players):
        wy_id = player['wyId']
        archetype = player['archetype']

        # Generate clamped radar scores
        radar_scores = {}
        for cat_name in category_names:
            z = z_matrix[cat_name][i]
            radar_scores[cat_name] = clamp_40_90(z)

        # STEP 3: Overall = weighted average of THESE EXACT clamped scores
        weights = weight_tables.get(archetype, weight_tables.get("CM / DM", weight_tables.get("GK", {})))
        if not weights:
            weights = {cat: 1.0 / len(category_names) for cat in category_names}

        overall_raw = 0.0
        total_w = 0.0
        for cat, w in weights.items():
            overall_raw += radar_scores.get(cat, 65) * w
            total_w += w

        if total_w > 0:
            overall_raw /= total_w
            overall_raw *= total_w  # This is already correct since sum of weights = ~1.0

        # Because all inputs are [40,90] and weights sum to ~1.0,
        # the weighted average is mathematically guaranteed to be [40,90]
        overall_rating = int(math.floor(max(40, min(90, overall_raw))))

        # Top traits (highest clamped categories)
        sorted_cats = sorted(radar_scores.items(), key=lambda x: x[1], reverse=True)
        top_traits = [sorted_cats[0][0], sorted_cats[1][0]] if len(sorted_cats) >= 2 else [sorted_cats[0][0]] if sorted_cats else []

        # Liability warning
        stats = player['normalized_stats']
        liability = None
        dohl = stats.get('dangerousOwnHalfLosses', 0)
        if dohl and dohl > 1.5:
            liability = "High risk of losing ball in own half"
        elif stats.get('yellowCards', 0) > 0 and stats.get('percent.yellowCardsPerFoul', 0) > 25:
            liability = "Prone to reckless tackling (High Cards/Foul)"

        results[wy_id] = {
            'radarScores': radar_scores,
            'overallRating': overall_rating,
            'topTraits': top_traits,
            'liabilityWarning': liability,
        }

    return results
