import os
import json
import pandas as pd
import numpy as np
from scipy.stats import zscore
from collections import defaultdict
import math

DATA_DIR = "./Date - meciuri"

TACTICAL_SYSTEMS = {
    "tiki_taka": {
        "name": "Tiki-Taka (Possession)",
        "weights": {
            "z_total_successfulPasses": 2.5,
            "z_total_smartPasses": 2.0,
            "z_total_receivedPass": 1.5,
            "z_total_losses": -1.5
        }
    },
    "gegenpressing": {
        "name": "Gegenpressing (High Press)",
        "weights": {
            "z_total_pressingDuelsWon": 2.5,
            "z_total_interceptions": 2.0,
            "z_total_accelerations": 1.5,
            "z_total_counterpressingRecoveries": 2.0
        }
    },
    "counter_attack": {
        "name": "Counter-Attack",
        "weights": {
            "z_total_progressiveRun": 2.5,
            "z_total_successfulLongPasses": 2.0,
            "z_total_forwardPasses": 1.5
        }
    }
}

def safe_div(a, b):
    return a / b if b and b > 0 else 0

def load_data_to_dataframe() -> pd.DataFrame:
    all_player_stats = []
    
    for filename in os.listdir(DATA_DIR):
        if not filename.endswith("players_stats.json"):
            continue
            
        file_path = os.path.join(DATA_DIR, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for player in data.get("players", []):
                wyId = player.get("playerId")
                positions = player.get("positions", [])
                primary_code = positions[0].get("position", {}).get("code", "Unknown").lower() if positions else "Unknown"
                
                total = player.get("total", {})
                percent = player.get("percent", {})
                
                # We flatten stats into a dict
                stat_entry = {"wyId": wyId, "rawPosition": primary_code}
                for k, v in total.items():
                    stat_entry[f"total_{k}"] = v
                for k, v in percent.items():
                    stat_entry[f"percent_{k}"] = v
                    
                all_player_stats.append(stat_entry)
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            
    # Aggregate stats per player (sum totals, average percents weighted by matches or just take max if pre-aggregated)
    # Actually, Wyscout JSONs per match have match stats. To get season stats, we must sum totals.
    # Wait, the current `process_match_files` in ingestion.py handles summation of totals and weighted averages of percents.
    
    # It's better to use the already aggregated dictionary from ingestion.py, OR we rewrite it here in pandas.
    df = pd.DataFrame(all_player_stats)
    
    if df.empty:
        return df

    # Fill NaNs
    df.fillna(0, inplace=True)
    
    # Group by wyId
    # Sum all 'total_' columns
    total_cols = [c for c in df.columns if c.startswith('total_')]
    
    # Percents in per-match files cannot just be averaged. We must recalculate from successful/total if available.
    # However, for simplicity and since we want a Pandas pipeline:
    agg_funcs = {col: 'sum' for col in total_cols}
    agg_funcs['rawPosition'] = 'first' # Take the most frequent or first
    
    df_grouped = df.groupby('wyId').agg(agg_funcs).reset_index()
    
    return df_grouped

def run_pandas_pipeline(df: pd.DataFrame, master_positions_dict: dict) -> pd.DataFrame:
    """
    Takes the grouped Pandas DataFrame from ingestion.py,
    calculates CAI, True Yield, Positional Z-Scores, and FSR.
    """
    if df.empty:
        return df
        
    # Map normalized positions
    df['master_position'] = df['wyId'].map(master_positions_dict)
    
    # Fill missing
    df.fillna(0, inplace=True)
    
    # 1. Calculate CAI (Consistency & Availability Index)
    # (Total Minutes / (Matches * 90))
    # Bonus 1.1x if Start Ratio > 75%
    # Penalty exponential if Avg Minutes/Match < 35
    
    def calc_cai(row):
        matches = row.get('total_matches', 0)
        minutes = row.get('total_minutesOnField', 0)
        starts = row.get('total_matchesInStart', 0)
        
        if matches == 0:
            return 0.0
            
        cai = minutes / (matches * 90.0)
        
        start_ratio = starts / matches
        if start_ratio > 0.75:
            cai *= 1.1
            
        avg_minutes = minutes / matches
        if avg_minutes < 35:
            cai *= math.exp(- (35 - avg_minutes) / 10.0) # exponential decay
            
        return min(cai, 1.5) # Cap at 1.5
        
    df['CAI'] = df.apply(calc_cai, axis=1)
    
    # 2. True Yield
    # (Successful / Total) * log(Total + 2) * ActionWeight
    # We will compute a unified 'TrueYield_Offense' and 'TrueYield_Defense' based on key metrics.
    
    def calc_true_yield(total_actions, percent_successful, weight):
        successful = total_actions * (percent_successful / 100.0)
        if total_actions == 0:
            return 0.0
        return (successful / total_actions) * np.log(total_actions + 2) * weight

    df['TY_Passes'] = df.apply(lambda r: calc_true_yield(r.get('total_passes', 0), r.get('percent_successfulPasses', 0), 1.0), axis=1)
    df['TY_DefDuels'] = df.apply(lambda r: calc_true_yield(r.get('total_defensiveDuels', 0), r.get('percent_defensiveDuelsWon', 0), 1.5), axis=1)
    df['TY_OffDuels'] = df.apply(lambda r: calc_true_yield(r.get('total_offensiveDuels', 0), r.get('percent_offensiveDuelsWon', 0), 1.5), axis=1)
    
    # 3. Positional Z-Scores
    # We Z-Score key metrics specifically grouped by 'master_position'
    
    metrics_to_zscore = [
        'TY_Passes', 'TY_DefDuels', 'TY_OffDuels', 'CAI',
        'total_goals', 'total_assists', 'total_interceptions',
        'total_successfulPasses', 'total_smartPasses', 'total_receivedPass', 'total_losses',
        'total_pressingDuelsWon', 'total_accelerations', 'total_counterpressingRecoveries',
        'total_progressiveRun', 'total_successfulLongPasses', 'total_forwardPasses'
    ]
    
    for metric in metrics_to_zscore:
        if metric not in df.columns:
            df[metric] = 0.0
            
        # Compute positional Z-Score
        df[f'z_{metric}'] = df.groupby('master_position')[metric].transform(
            lambda x: zscore(x, nan_policy='omit') if len(x) > 1 and x.std() > 0 else 0.0
        )
        
    # 4. Positional Weights & Final Scouting Rating (FSR)
    def calc_fsr(row):
        pos = row['master_position']
        
        # Base Z-Score summation based on position priorities
        if pos in ['CB', 'LB', 'RB']:
            score = row['z_TY_DefDuels'] * 2.0 + row['z_total_interceptions'] * 1.5 + row['z_CAI'] * 1.0
        elif pos in ['CDM', 'CM']:
            score = row['z_TY_Passes'] * 2.0 + row['z_TY_DefDuels'] * 1.0 + row['z_CAI'] * 1.0
        elif pos in ['CAM', 'LM', 'RM', 'LW', 'RW']:
            score = row['z_TY_OffDuels'] * 1.5 + row['z_total_assists'] * 2.0 + row['z_TY_Passes'] * 1.0
        elif pos in ['ST']:
            score = row['z_total_goals'] * 3.0 + row['z_TY_OffDuels'] * 1.0 + row['z_CAI'] * 1.0
        elif pos in ['GK']:
            score = row['z_CAI'] * 1.0 # Simplified for GK
        else:
            score = row['z_CAI'] * 1.0
            
        return score

    df['raw_FSR'] = df.apply(calc_fsr, axis=1)
    
    # Normalize FSR to 0-100 scale using Min-Max scaling per position, or globally.
    # We'll do it per position to ensure we always have a 100 rated ST and a 100 rated CB.
    def min_max_scale(x):
        if x.max() == x.min():
            return pd.Series(50.0, index=x.index)
        return (x - x.min()) / (x.max() - x.min()) * 100.0

    df['FSR'] = df.groupby('master_position')['raw_FSR'].transform(min_max_scale)
    
    return df

def calculate_tactical_fit(row, system_id):
    if system_id not in TACTICAL_SYSTEMS:
        return 0.0
        
    system = TACTICAL_SYSTEMS[system_id]
    weights = system["weights"]
    
    fit_score = 0
    total_weight = 0
    
    for z_metric, weight in weights.items():
        val = row.get(z_metric, 0)
        # We cap Z-score contribution between -3 and 3 for stability
        contribution = max(min(val, 3), -3) * weight
        fit_score += contribution
        total_weight += abs(weight)
        
    if total_weight == 0:
        return 0.0
        
    # Map the fit score to a 0-100 percentage. 
    # A score of 0 (average) should be around 50%.
    # A score of 2.0 (strong outlier) should be high 90s.
    percentage = 50 + (fit_score / total_weight) * 25
    return max(min(round(percentage, 1), 100.0), 0.0)
