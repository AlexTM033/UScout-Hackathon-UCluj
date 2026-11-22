from typing import List, Dict, Any
import random

# Local fallback benchmarks for trait discovery if no population data available
FALLBACK_BENCHMARKS = {
    "xgShot": 0.5, "goals": 0.4, "shots": 3.0, "touchInBox": 5.0,
    "smartPasses": 1.2, "progressivePasses": 8.0, "interceptions": 5.0,
    "recoveries": 8.0, "progressiveRun": 3.0, "accelerations": 2.5
}

def generate_scouting_analysis(player_id: int, position_code: str, normalized_stats: Dict[str, Any]) -> Dict[str, Any]:
    """
    Dynamic Relative Insights & Trait Generator
    Finds a player's personal best/worst traits relative to their position and generates dynamic phrases.
    """
    pos = (position_code or "").lower()
    
    # Step 1: Positional Priority Filtering
    if any(p in pos for p in ["st", "cf", "lw", "rw", "winger", "forward"]):
        priority_stats = ["xgShot", "touchInBox", "percent.shotsOnTarget", "percent.offensiveDuelsWon", "progressiveRun", "xgAssist", "accelerations"]
        role_type = "attacker"
    elif any(p in pos for p in ["cm", "dm", "am", "mid"]):
        priority_stats = ["smartPasses", "progressivePasses", "passesToFinalThird", "interceptions", "losses", "percent.successfulPasses"]
        role_type = "midfielder"
    elif any(p in pos for p in ["cb", "fb", "lb", "rb", "back", "defender"]):
        priority_stats = ["percent.defensiveDuelsWon", "percent.aerialDuelsWon", "interceptions", "percent.dribblesAgainstWon", "clearances"]
        role_type = "defender"
    else:
        priority_stats = ["percent.successfulPasses", "interceptions", "recoveries", "progressivePasses"]
        role_type = "general"

    # Step 2: Personal Relative Strength Ranking
    stat_rankings = []
    for stat_key in priority_stats:
        val = normalized_stats.get(stat_key, 0)
        benchmark = FALLBACK_BENCHMARKS.get(stat_key, 1.0)
        if benchmark == 0: benchmark = 0.01
        
        # Calculate ratio (Relative performance)
        # Note: for 'losses', 'yellowCards', etc., lower is better, so we invert the ratio
        is_inverse = stat_key in ["losses", "dangerousOwnHalfLosses", "yellowCards"]
        ratio = (benchmark / val if val > 0 else 2.0) if is_inverse else (val / benchmark)
        
        stat_rankings.append({
            "key": stat_key,
            "val": val,
            "ratio": ratio
        })

    # Sort by ratio descending (Best to Worst)
    stat_rankings.sort(key=lambda x: x["ratio"], reverse=True)
    
    top_stats = stat_rankings[:3]
    bottom_stats = stat_rankings[-3:]
    # Reverse bottom stats so the WORST is first
    bottom_stats.reverse()

    # Step 3: Dynamic Phrase Generation
    PRO_TEMPLATES = {
        "xgShot": ["Elite goal-scoring instincts with a high volume of quality chances", "Consistently finds himself in high-value scoring positions"],
        "touchInBox": ["Highly threatening inside the penalty area", "Exceptional at finding space in congested boxes"],
        "percent.shotsOnTarget": ["Exceptional shot accuracy and precision", "Highly efficient finisher with a clinical edge"],
        "percent.offensiveDuelsWon": ["Dominates offensive duels with physical presence", "Aggressive and successful in 1v1 attacking situations"],
        "progressiveRun": ["Elite progressive runner who drives the team forward", "Explosive transition threat when carrying the ball"],
        "xgAssist": ["Creative mastermind in the final third with elite underlying numbers", "Consistently creates high-quality scoring opportunities for teammates"],
        "accelerations": ["Possesses explosive acceleration that unbalances defenses", "Elite burst of speed in transition phases"],
        "smartPasses": ["Dissects defenses with visionary smart passes", "Exceptional at breaking defensive lines with creative distribution"],
        "progressivePasses": ["Elite ball progression via incisive forward passing", "Highly effective at advancing play into dangerous areas"],
        "passesToFinalThird": ["Exceptional at recycling possession into the final third", "Consistent source of entry passes into attacking zones"],
        "interceptions": ["Masterful reader of the game with elite interception volume", "Exceptional at anticipating and cutting out opposition passing lanes"],
        "losses": ["Highly reliable ball retention and security", "Exceptionally press-resistant and rarely loses possession"],
        "percent.successfulPasses": ["Highly reliable and press-resistant distributor", "Exceptional ball retention with elite pass completion"],
        "percent.defensiveDuelsWon": ["Brick wall in 1v1 defensive duels", "Tough tackle winner who dominates defensive challenges"],
        "percent.aerialDuelsWon": ["Dominant in aerial battles and set-piece situations", "Exceptional aerial presence both defensively and offensively"],
        "percent.dribblesAgainstWon": ["Highly reliable in 1v1 isolation situations", "Exceptional at tracking and neutralizing opposition dribblers"],
        "clearances": ["Masterful defensive positioning and clearance timing", "Highly reliable at neutralizing danger in the defensive third"],
        "recoveries": ["High-volume recovery generator in key areas", "Exceptional at winning back possession in transitions"]
    }

    CON_TEMPLATES = {
        "xgShot": ["Fails to find high-value scoring positions consistently", "Limited goal threat due to low expected goals output"],
        "touchInBox": ["Struggles to accumulate touches in the penalty area", "Often isolated from attacking play in the final third"],
        "percent.shotsOnTarget": ["Struggles with shot accuracy and finishing precision", "Needs to improve composure in front of goal"],
        "percent.offensiveDuelsWon": ["Lacks physical presence in offensive duels", "Often outmuscled in 1v1 attacking situations"],
        "progressiveRun": ["Lacks dribbling threat and ball-carrying drive", "Predictable ball carrier with limited transition impact"],
        "xgAssist": ["Limited creativity in key areas of the pitch", "Underwhelming underlying numbers for chance creation"],
        "accelerations": ["Limited mobility and burst of speed in transition", "Struggles to unbalance defenses with pace"],
        "smartPasses": ["Ineffective final ball and limited creative vision", "Struggles to break lines with incisive passing"],
        "progressivePasses": ["Struggles to advance play into the final third via passing", "Often opts for safe, sideways distribution"],
        "passesToFinalThird": ["Limited contribution to advancing play into the final third", "Needs to improve accuracy of entry passes"],
        "interceptions": ["Struggles with defensive positioning and anticipation", "Often fails to cut out opposition passing lanes"],
        "losses": ["Prone to costly turnovers and ball losses", "Struggles under pressure, leading to frequent loss of possession"],
        "percent.successfulPasses": ["Prone to unforced errors in distribution", "Underwhelming ball retention in contested areas"],
        "percent.defensiveDuelsWon": ["Liability in defensive duels and 1v1 situations", "Often second-best in physical defensive challenges"],
        "percent.aerialDuelsWon": ["Weak in the air and prone to losing aerial duels", "Vulnerable on set pieces and high-ball situations"],
        "percent.dribblesAgainstWon": ["Struggles when isolated against skilled dribblers", "Easily bypassed in 1v1 defensive situations"],
        "clearances": ["Struggles with defensive timing and clearance precision", "Can be hesitant when neutralizing danger in the box"],
        "recoveries": ["Underwhelming volume of ball recoveries in transitions", "Slow to react to loose ball situations"]
    }

    pros = []
    for s in top_stats:
        if s["key"] in PRO_TEMPLATES:
            phrase = random.choice(PRO_TEMPLATES[s["key"]])
            pros.append(phrase)
    
    cons = []
    for s in bottom_stats:
        if s["key"] in CON_TEMPLATES:
            phrase = random.choice(CON_TEMPLATES[s["key"]])
            cons.append(phrase)

    # Step 4: Enforce Variety and Limits
    # Pros: 2-3, Cons: 1-3
    final_pros = pros[:3] if len(pros) >= 2 else (pros + ["Reliable ball retention with consistent pass completion."])[:2]
    final_cons = cons[:3] if len(cons) >= 1 else ["Area for improvement in overall tactical consistency."]

    return {
        "playerId": player_id,
        "evaluatedPosition": pos,
        "scoutingAnalysis": {
            "pros": final_pros,
            "cons": final_cons
        }
    }
