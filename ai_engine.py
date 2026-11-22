import os
import json
import pickle
import pandas as pd
from scipy.spatial.distance import cosine
import google.generativeai as genai
from sqlalchemy.orm import Session
from database import Player, PlayerStats
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_similar_players(wyId: int) -> list:
    from ingestion import _global_advanced_metrics_df
    
    if _global_advanced_metrics_df is None or _global_advanced_metrics_df.empty:
        return []
        
    df = _global_advanced_metrics_df
    
    if wyId not in df['wyId'].values:
        return []
        
    target_row = df[df['wyId'] == wyId].iloc[0]
    position = target_row['master_position']
    
    pool = df[df['master_position'] == position].copy()
    pool = pool[pool['wyId'] != wyId]
    
    if pool.empty:
        return []
        
    z_cols = [c for c in df.columns if c.startswith('z_')]
    
    if not z_cols:
        return []
        
    target_vector = target_row[z_cols].values
    
    similarities = []
    for _, row in pool.iterrows():
        candidate_vector = row[z_cols].values
        if (target_vector == 0).all() or (candidate_vector == 0).all():
            dist = 1.0
        else:
            dist = cosine(target_vector, candidate_vector)
        similarity = 1 - dist
        
        similarities.append({
            "wyId": int(row['wyId']),
            "similarity": float(similarity),
            "FSR": float(row['FSR']),
            "z_scores": row[z_cols].to_dict()
        })
        
    similarities.sort(key=lambda x: x['similarity'], reverse=True)
    return similarities[:3]


def _get_behavioral_stats(player_id: int) -> dict:
    """Extract raw behavioral stats from processed_metrics.pkl for LLM analysis."""
    try:
        df = pickle.load(open("processed_metrics.pkl", "rb"))
        row = df[df['wyId'] == player_id]
        if row.empty:
            return {}
        row = row.iloc[0]
        
        minutes = row.get('total_minutesOnField', 0)
        matches = row.get('total_matches', 0) or 1
        
        return {
            "minutesPlayed": int(minutes),
            "matches": int(matches),
            "yellowCards": int(row.get('total_yellowCards', 0)),
            "redCards": int(row.get('total_redCards', 0)),
            "directRedCards": int(row.get('total_directRedCards', 0)),
            "foulsCommitted": int(row.get('total_fouls', 0)),
            "foulsSuffered": int(row.get('total_foulsSuffered', 0)),
            "pressingDuels": int(row.get('total_pressingDuels', 0)),
            "pressingDuelsWon": int(row.get('total_pressingDuelsWon', 0)),
            "counterpressingRecoveries": int(row.get('total_counterpressingRecoveries', 0)),
            "duelsTotal": int(row.get('total_duels', 0)),
            "duelsWon": int(row.get('total_duelsWon', 0)),
            "defensiveDuels": int(row.get('total_defensiveDuels', 0)),
            "defensiveDuelsWon": int(row.get('total_defensiveDuelsWon', 0)),
            "offensiveDuels": int(row.get('total_offensiveDuels', 0)),
            "offensiveDuelsWon": int(row.get('total_offensiveDuelsWon', 0)),
            "aerialDuels": int(row.get('total_aerialDuels', 0)),
            "aerialDuelsWon": int(row.get('total_aerialDuelsWon', 0)),
            "looseBallDuels": int(row.get('total_looseBallDuels', 0)),
            "looseBallDuelsWon": int(row.get('total_looseBallDuelsWon', 0)),
            "losses": int(row.get('total_losses', 0)),
            "ownHalfLosses": int(row.get('total_ownHalfLosses', 0)),
            "dangerousOwnHalfLosses": int(row.get('total_dangerousOwnHalfLosses', 0)),
            "yellowCardsPerFoul": float(row.get('percent_yellowCardsPerFoul', 0)),
            "duelsWonPct": float(row.get('percent_duelsWon', 0)),
            "defensiveDuelsWonPct": float(row.get('percent_defensiveDuelsWon', 0)),
        }
    except Exception as e:
        print(f"[ai_engine] Could not load behavioral stats: {e}")
        return {}


def _rule_based_personality(behavioral: dict, captain_count: int, position: str) -> dict:
    """Generate personality traits using rule-based logic when LLM is unavailable."""
    traits = []
    reasons = []
    
    minutes = behavioral.get('minutesPlayed', 0)
    yellows = behavioral.get('yellowCards', 0)
    reds = behavioral.get('directRedCards', 0) + behavioral.get('redCards', 0)
    fouls = behavioral.get('foulsCommitted', 0)
    fouls_suffered = behavioral.get('foulsSuffered', 0)
    pressing = behavioral.get('pressingDuels', 0)
    pressing_won = behavioral.get('pressingDuelsWon', 0)
    counter_press = behavioral.get('counterpressingRecoveries', 0)
    duels_pct = behavioral.get('duelsWonPct', 0)
    losses = behavioral.get('losses', 0)
    own_half_losses = behavioral.get('dangerousOwnHalfLosses', 0)
    
    matches = behavioral.get('matches', 0) or 1
    fouls_p90 = (fouls / minutes * 90) if minutes > 0 else 0
    yellows_per_match = yellows / matches
    
    # Leadership
    if captain_count >= 3:
        traits.append("Lider Natural")
        reasons.append(f"Căpitan în {captain_count} meciuri — demonstrează leadership constant.")
    elif captain_count >= 1:
        traits.append("Lider Tacit")
        reasons.append(f"Experiență de căpitănie ({captain_count} meciuri).")
    
    # Aggression vs Discipline
    if yellows_per_match > 0.35 or reds >= 2:
        traits.append("Agresiv")
        reasons.append(f"{yellows} galbene, {reds} roșii — jucător combativ, depășește frecvent limita.")
    elif fouls_p90 > 1.5:
        traits.append("Combativ")
        reasons.append(f"{fouls_p90:.1f} faulturi/90 min — implicare fizică intensă.")
    elif fouls_p90 < 0.5 and yellows_per_match < 0.1:
        traits.append("Calculat")
        reasons.append(f"Foarte rar sancționat ({yellows} galbene) — joc curat și inteligent.")
    else:
        traits.append("Disciplinat")
        reasons.append(f"Profil disciplinar echilibrat ({yellows} galbene în {matches} meciuri).")
    
    # Pressing / Work rate
    if pressing > 0 and minutes > 0:
        pressing_p90 = pressing / minutes * 90
        if pressing_p90 > 6:
            traits.append("Motor")
            reasons.append(f"Pressing intens ({pressing_p90:.1f}/90 min) — acoperă mult teren.")
        elif pressing_p90 > 3:
            traits.append("Muncitor")
            reasons.append(f"Contribuție constantă în pressing ({pressing_p90:.1f}/90 min).")
    
    # Foul drawing / Provocator
    if fouls_suffered > fouls * 1.5 and fouls_suffered > 15:
        if "Agresiv" not in traits:
            traits.append("Provocator")
            reasons.append(f"Atrage {fouls_suffered} faulturi — destabilizează adversarii.")
    
    # Dueling mentality
    if duels_pct > 58:
        if len(traits) < 3:
            traits.append("Dominant Fizic")
            reasons.append(f"Câștigă {duels_pct:.0f}% din dueluri — prezență fizică impunătoare.")
    elif duels_pct < 42 and minutes > 500:
        if len(traits) < 3:
            traits.append("Vulnerabil")
            reasons.append(f"Câștigă doar {duels_pct:.0f}% din dueluri — expus în confruntări directe.")
    
    # Ball security
    if own_half_losses > 15 and minutes > 500:
        if len(traits) < 3:
            traits.append("Imprevizibil")
            reasons.append(f"{own_half_losses} pierderi periculoase — risc de turnover.")
    
    # Ensure we have 2-3 traits
    if len(traits) < 2:
        traits.append("Profesionist")
        reasons.append("Profil stabil, fără abateri notabile.")
    
    traits = traits[:3]
    reasons = reasons[:3]
    
    summary = " ".join(reasons)
    # Enforce 150-char limit
    if len(summary) > 150:
        summary = summary[:147] + "..."
    return {"traits": traits, "summary": summary}


def _rule_based_tactical_fit(behavioral: dict, radar: dict, position: str) -> dict:
    """Generate tactical fit score using rule-based logic."""
    score = 70
    
    # Physical league — reward pressing and duels
    pressing = behavioral.get('pressingDuels', 0)
    minutes = behavioral.get('minutesPlayed', 0)
    duels_pct = behavioral.get('duelsWonPct', 0)
    
    if pressing > 0 and minutes > 0:
        pressing_p90 = pressing / minutes * 90
        if pressing_p90 > 5:
            score += 10
        elif pressing_p90 > 3:
            score += 5
    
    if duels_pct > 55:
        score += 8
    elif duels_pct > 50:
        score += 3
    
    # Use radar scores if available
    if radar:
        physicality = radar.get('Physicality', 50)
        defending = radar.get('Defending', 50)
        if physicality > 70:
            score += 5
        if defending > 70:
            score += 5
    
    score = min(98, max(30, score))
    status = "OPTIM" if score >= 75 else ("MEDIU" if score >= 55 else "CRITIC")
    
    return {
        "score": score,
        "status": status,
        "description": f"Evaluare bazată pe profilul comportamental ({behavioral.get('duelsTotal', 0)} dueluri, {behavioral.get('pressingDuels', 0)} pressing)."
    }


def generate_integration_report(player_id: int, db: Session) -> dict:
    from csv_lookup import player_match_optimizer, get_transfer_history
    from datetime import datetime

    # 1. Get Player and Stats
    player = db.query(Player).filter(Player.wyId == player_id).first()
    if not player:
        return {}
    
    stats_record = db.query(PlayerStats).filter(PlayerStats.wyId == player_id).first()
    
    # 2. Get TM Data and Transfers
    tm_data = player_match_optimizer(player.firstName or '', player.lastName or '')
    tm_id = tm_data.get('player_id')
    transfers = get_transfer_history(tm_id)
    
    # 3. Get behavioral stats from processed_metrics.pkl
    behavioral = _get_behavioral_stats(player_id)
    
    # 4. Factor 1: Geographical/Cultural
    nat = tm_data.get('nationality', 'Unknown')
    low_risk_regions = ["Romania", "Bulgaria", "Serbia", "Moldova", "Hungary", "Ukraine", 
                        "Poland", "Croatia", "Slovenia", "Montenegro", "Albania", "Macedonia"]
    
    geo_score = 100
    geo_status = "OPTIM"
    geo_desc = f"Jucătorul este din {nat}, o regiune cu proximitate culturală ridicată."
    
    if any(region in str(nat) for region in low_risk_regions):
        geo_score = 95
    elif any(region in str(nat) for region in ["Brazil", "Argentina", "Colombia", "Ecuador", "Chile"]):
        geo_score = 45
        geo_status = "CRITIC"
        geo_desc = f"Provine din {nat}. Necesită timp de acomodare pentru climă și cultură."
    else:
        geo_score = 70
        geo_status = "MEDIU"
        geo_desc = "Adaptare culturală standard pentru profilul european."

    # 5. Factor 2: Stability (Transfer Frequency)
    stability_score = 85
    stability_status = "OPTIM"
    stability_desc = "Istoric de transferuri echilibrat."
    
    if len(transfers) >= 2:
        dates = []
        for t in transfers:
            if t.get('date'):
                try:
                    dates.append(datetime.strptime(t['date'], "%Y-%m-%d"))
                except:
                    pass
        
        if len(dates) >= 2:
            dates.sort()
            diffs = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
            avg_days = sum(diffs) / len(diffs)
            avg_years = avg_days / 365
            
            if avg_years < 0.9: 
                stability_score = 35
                stability_status = "CRITIC"
                stability_desc = f"Frecvență mare de transferuri ({avg_years:.1f} ani medie). Posibilă instabilitate."
            elif avg_years < 1.6:
                stability_score = 65
                stability_status = "MEDIU"
                stability_desc = f"Carieră dinamică ({avg_years:.1f} ani medie)."
            else:
                stability_score = 98
                stability_desc = f"Stabilitate excelentă ({avg_years:.1f} ani medie)."

    # 6. Extract Captaincy from game_lineups.csv
    captain_count = 0
    lineups_path = os.path.join("transfermarkt-datasets", "game_lineups.csv")
    if tm_id and os.path.exists(lineups_path):
        try:
            import csv
            with open(lineups_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('player_id') == str(tm_id) and row.get('team_captain') == '1':
                        captain_count += 1
        except:
            pass

    # 7. Parse radar scores
    ui_stats = {}
    if stats_record and stats_record.normalized_stats:
        ui_stats = json.loads(stats_record.normalized_stats)
    radar = ui_stats.get('radarScores', {})
    position = player.positionCode or ''
    
    # 8. LLM Call with Behavioral Context
    llm_success = False
    ai_data = {}
    
    try:
        prompt = f"""Ești un expert în psihologie sportivă și scouting de fotbal. 
Analizează datele comportamentale ale jucătorului {player.firstName} {player.lastName} ({position}).

DATE COMPORTAMENTALE DIN MECIURI REALE:
- Minute jucate: {behavioral.get('minutesPlayed', 0)}
- Meciuri: {behavioral.get('matches', 0)}
- Cartonașe galbene: {behavioral.get('yellowCards', 0)} | Roșii directe: {behavioral.get('directRedCards', 0)}
- Faulturi comise: {behavioral.get('foulsCommitted', 0)} | Faulturi suferite: {behavioral.get('foulsSuffered', 0)}
- Dueluri totale: {behavioral.get('duelsTotal', 0)} (câștigate: {behavioral.get('duelsWonPct', 0):.0f}%)
- Pressing duels: {behavioral.get('pressingDuels', 0)} (câștigate: {behavioral.get('pressingDuelsWon', 0)})
- Counterpressing recoveries: {behavioral.get('counterpressingRecoveries', 0)}
- Pierderi propria jumătate: {behavioral.get('dangerousOwnHalfLosses', 0)}
- Meciuri ca și căpitan: {captain_count}

RADAR SCORES: {json.dumps(radar)}

INSTRUCȚIUNI STRICTE:
1. Dedu 2-3 trăsături VARIATE de personalitate pe teren (ex: "Lider Natural", "Agresiv", "Calculat", "Muncitor", "Provocator", "Imprevizibil", "Introvertit", "Dominant Fizic")
2. Scrie un rezumat SCURT de MAXIM 2 propoziții, MAXIM 150 caractere total. Citează statistici concrete.
3. Returnează DOAR un JSON valid, fără markdown:
{{"traits": ["Trait1", "Trait2"], "summary": "Max 150 chars..."}}
"""
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        clean_text = response.text.strip().replace("```json", "").replace("```", "").strip()
        personality_data = json.loads(clean_text)
        
        # Validate structure
        if isinstance(personality_data.get('traits'), list) and isinstance(personality_data.get('summary'), str):
            # Enforce 150-char limit on LLM output
            s = personality_data['summary']
            if len(s) > 150:
                personality_data['summary'] = s[:147] + '...'
            ai_data['personality'] = personality_data
            llm_success = True
    except Exception as e:
        print(f"[ai_engine] LLM personality error: {e}")
    
    if not llm_success:
        ai_data['personality'] = _rule_based_personality(behavioral, captain_count, position)
    
    # 9. Tactical Fit (LLM or Rule-based)
    try:
        if llm_success:
            # Try a second LLM call for tactical fit
            tac_prompt = f"""Evaluează compatibilitatea tactică a jucătorului {player.firstName} {player.lastName} ({position}) pentru Superliga României (campionat fizic, dueluri aeriene, tranziții rapide).

Radar: {json.dumps(radar)}
Dueluri câștigate: {behavioral.get('duelsWonPct', 0):.0f}%, Pressing/90: {(behavioral.get('pressingDuels', 0) / max(behavioral.get('minutesPlayed', 1), 1) * 90):.1f}

Returnează DOAR JSON valid:
{{"score": 0-100, "status": "OPTIM"|"MEDIU"|"CRITIC", "description": "scurt text"}}"""
            
            response2 = model.generate_content(tac_prompt)
            clean2 = response2.text.strip().replace("```json", "").replace("```", "").strip()
            ai_data['tacticalFit'] = json.loads(clean2)
        else:
            raise Exception("Skip LLM")
    except:
        ai_data['tacticalFit'] = _rule_based_tactical_fit(behavioral, radar, position)

    # 10. Factor 4: Experience/Age
    age = 25
    if player.birthDate:
        try:
            bd = datetime.strptime(player.birthDate, "%Y-%m-%d")
            age = (datetime.now() - bd).days // 365
        except:
            pass
        
    exp_score = 80
    exp_status = "OPTIM"
    exp_desc = f"Experiență potrivită pentru maturitate sportivă ({age} ani)."
    if age < 22:
        exp_score = 55
        exp_status = "MEDIU"
        exp_desc = f"Jucător în formare ({age} ani). Necesită mentorat."
    elif age > 33:
        exp_score = 85
        exp_desc = f"Veteran cu experiență vastă ({age} ani)."

    # 11. Final Risk Calculation
    tac_score = ai_data['tacticalFit']['score']
    avg_score = (geo_score + stability_score + tac_score + exp_score) / 4
    risk_percentage = int(100 - avg_score)
    
    # 12. AI Decision Matrix (Pros & Cons from DB scouting analysis)
    ai_pros = []
    ai_cons = []
    if ui_stats.get('scoutingAnalysis'):
        sa = ui_stats['scoutingAnalysis']
        ai_pros = sa.get('pros', [])[:3]
        ai_cons = sa.get('cons', [])[:3]
    
    # Enrich with radar-based insights if scoutingAnalysis is empty
    if not ai_pros and radar:
        for k, v in radar.items():
            if v >= 70:
                ai_pros.append(f"Aptitudine remarcabilă: {k} ({v})")
            if len(ai_pros) >= 3:
                break
    if not ai_cons and radar:
        for k, v in radar.items():
            if v < 50:
                ai_cons.append(f"Deficit semnificativ: {k} ({v})")
            if len(ai_cons) >= 3:
                break
    
    if not ai_pros:
        ai_pros = ["Performanțe echilibrate pe toate planurile."]
    if not ai_cons:
        ai_cons = ["Fără puncte slabe majore identificate."]
    
    return {
        "riskPercentage": max(0, min(100, risk_percentage)),
        "factors": [
            {"title": "Bariera Lingvistică & Culturală", "status": geo_status, "score": geo_score, "description": geo_desc},
            {"title": "Stabilitate Cariera", "status": stability_status, "score": stability_score, "description": stability_desc},
            {"title": "Adaptabilitate Tactică Superliga", "status": ai_data['tacticalFit']['status'], "score": tac_score, "description": ai_data['tacticalFit']['description']},
            {"title": "Maturitate și Experiență", "status": exp_status, "score": exp_score, "description": exp_desc}
        ],
        "personality": ai_data['personality'],
        "aiDecisionMatrix": {
            "pros": ai_pros,
            "cons": ai_cons
        }
    }


def generate_scouting_report(target_wyId: int, query: str, db: Session) -> str:
    similar_players_data = get_similar_players(target_wyId)
    enhanced_data = []
    for sp in similar_players_data:
        p = db.query(Player).filter(Player.wyId == sp['wyId']).first()
        if p:
            sp['name'] = f"{p.firstName} {p.lastName}".strip()
            enhanced_data.append(sp)
            
    tp = db.query(Player).filter(Player.wyId == target_wyId).first()
    target_name = f"{tp.firstName} {tp.lastName}".strip() if tp else str(target_wyId)
    
    context_json = json.dumps(enhanced_data, indent=2)
    system_instruction = (
        "You are an elite football scout. The user asked a question about "
        f"finding players similar to {target_name}. "
        "Based ONLY on the provided JSON data of similar players found in our database, "
        "answer the user in a professional, analytical tone, highlighting why these players "
        "are a good match mathematically."
    )
    
    prompt = f"System Instruction:\n{system_instruction}\n\nData Context:\n{context_json}\n\nUser Query:\n{query}"
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(prompt)
    return response.text

def generate_tactical_dna(player_id: int, db: Session) -> dict:
    from database import Player, PlayerStats
    from scraper import get_market_value
    import json
    
    player = db.query(Player).filter(Player.wyId == player_id).first()
    if not player:
        return {}
        
    stats_record = db.query(PlayerStats).filter(PlayerStats.wyId == player_id).first()
    if not stats_record or not stats_record.normalized_stats:
        return {}
        
    stats_json = json.loads(stats_record.normalized_stats)
    radar = stats_json.get('radarScores', {})
    
    shooting = radar.get('Shooting', 50)
    passing = radar.get('Passing', 50)
    dribbling = radar.get('Dribbling', 50)
    defending = radar.get('Defending', 50)
    physicality = radar.get('Physicality', 50)
    mentality = radar.get('Mentality', 50)
    
    pos = str(player.positionCode).upper()
    
    metrics = []
    position_matched = "Necunoscut"
    
    if pos in ['ST', 'LW', 'RW', 'CF']:
        position_matched = "Atacant"
        if pos == 'ST': position_matched = "Atacant Central (ST)"
        elif pos == 'LW': position_matched = "Extremă Stânga (LW)"
        elif pos == 'RW': position_matched = "Extremă Dreapta (RW)"
        
        mappings = [
            ("Finalizare precisă", shooting, 75),
            ("Joc de cap & Dueluri", physicality, 65),
            ("Pressing imediat la pierdere", defending, 60),
            ("Poziționare & Spații libere", mentality, 70),
            ("Inițiere Contraatac", dribbling, 70),
            ("Disciplină tactică", passing, 65)
        ]
    elif pos in ['CM', 'CDM', 'CAM', 'RM', 'LM']:
        position_matched = "Mijlocaș"
        if pos == 'CM': position_matched = "Mijlocaș Central (CM)"
        elif pos == 'CDM': position_matched = "Mijlocaș Defensiv (CDM)"
        elif pos == 'CAM': position_matched = "Mijlocaș Ofensiv (CAM)"
        
        mappings = [
            ("Construcție sub presiune", passing, 75),
            ("Recuperare rapidă", defending, 70),
            ("Pase de ruptură", shooting, 70),
            ("Tranziție defensivă", physicality, 65),
            ("Efort susținut (Box-to-Box)", mentality, 70),
            ("Disciplină tactică", dribbling, 70)
        ]
    else: # Defenders & GK
        position_matched = "Fundaș / Portar"
        if pos == 'CB': position_matched = "Fundaș Central (CB)"
        elif pos == 'LB': position_matched = "Fundaș Stânga (LB)"
        elif pos == 'RB': position_matched = "Fundaș Dreapta (RB)"
        
        mappings = [
            ("Marcaj strict", defending, 75),
            ("Dueluri aeriene", physicality, 75),
            ("Ieșire cu mingea la picior", passing, 65),
            ("Blocaj & Intercepții", mentality, 70),
            ("Repliere defensivă", dribbling, 65),
            ("Curaj în dueluri", shooting, 70)
        ]
        
    total_fit_sum = 0
    
    for label, p_score, t_score in mappings:
        diff = p_score - t_score
        
        if diff >= 0:
            fit_pct = 100
        else:
            fit_pct = max(0, 100 - (abs(diff) * 2))
            
        metrics.append({
            "label": label,
            "playerScore": p_score,
            "targetScore": t_score,
            "difference": diff
        })
        total_fit_sum += fit_pct
        
    overall_fit = round(total_fit_sum / len(metrics)) if metrics else 0
    
    # Format biographical data
    age = "?"
    if player.birthDate:
        try:
            import datetime
            birth_year = int(player.birthDate.split('-')[0])
            age = str(datetime.datetime.now().year - birth_year)
        except:
            pass
            
    # Get club and market value via csv lookup
    from csv_lookup import player_match_optimizer
    csv_result = player_match_optimizer(player.firstName or '', player.lastName or '')
    
    club = csv_result.get('tm_club') or "Liber de contract"
    position_details = f"{pos} • {age} ani • {club}"
    
    # Format market value
    mv_str = "€0"
    if csv_result.get('market_value_raw'):
        try:
            v = float(csv_result['market_value_raw'])
            if v >= 1000000:
                mv_str = f"€{v/1000000:.1f}M"
            elif v >= 1000:
                mv_str = f"€{int(v/1000)}K"
            else:
                mv_str = f"€{int(v)}"
        except (ValueError, TypeError):
            pass
            
    name = f"{player.firstName} {player.lastName}".strip()
    if not name:
        name = player.shortName
    
    return {
        "player": {
            "id": player.wyId,
            "name": name,
            "positionDetails": position_details,
            "marketValue": mv_str
        },
        "tacticalEvaluation": {
            "positionMatched": position_matched,
            "overallFitPercentage": overall_fit,
            "metrics": metrics
        }
    }


def find_ai_twins(query: str, db: Session) -> dict:
    """
    AI Digital Twin Engine — 3-Phase Pipeline:
      Phase 1: Strict position pre-filter (exact primary position match)
      Phase 2: Cosine similarity on 6-dim radar vector (scipy)
      Phase 3: LLM summarization of top 3 (formatting only, no searching)
    """
    import json
    import datetime
    import unicodedata
    import numpy as np
    from scipy.spatial.distance import cosine as cosine_distance
    from database import Player, PlayerStats

    # ── Radar vector definition (strict order) ──
    VECTOR_KEYS = ["Shooting", "Passing", "Dribbling", "Defending", "Physicality", "Mentality"]

    def remove_accents(s):
        if not s:
            return ""
        return ''.join(c for c in unicodedata.normalize('NFD', s)
                       if unicodedata.category(c) != 'Mn')

    def extract_primary_position(pos_str):
        """Extract the first/primary position from compound strings like 'ST / CF' or 'LB / RB'."""
        if not pos_str:
            return None
        return pos_str.split('/')[0].strip().upper()

    def build_radar_vector(radar_dict):
        """Build a numpy array from radar scores in strict VECTOR_KEYS order."""
        return np.array([float(radar_dict.get(k, 50)) for k in VECTOR_KEYS], dtype=np.float64)

    # ══════════════════════════════════════════════════════════════
    # STEP 0: Parse the query to extract target player name
    # ══════════════════════════════════════════════════════════════
    query_clean = remove_accents(query.lower().strip())
    for filler in ["find me players like ", "players like ", "twin for ",
                    "similar to ", "like ", "asemanator cu ", "ca si "]:
        if query_clean.startswith(filler):
            query_clean = query_clean[len(filler):].strip()

    # Find the target player in the database
    players = db.query(Player).all()
    target_player = None
    for p in players:
        full_name = remove_accents(f"{p.firstName} {p.lastName}".lower().strip())
        short_name = remove_accents((p.shortName or "").lower().strip())
        if query_clean in full_name or query_clean in short_name:
            target_player = p
            break

    if not target_player:
        return None

    # Load target player's stats
    target_stats_obj = db.query(PlayerStats).filter(
        PlayerStats.wyId == target_player.wyId
    ).first()
    if not target_stats_obj or not target_stats_obj.normalized_stats:
        return None

    target_ns = json.loads(target_stats_obj.normalized_stats)
    target_radar = target_ns.get("radarScores", {})
    if not target_radar or len(target_radar) < 4:
        return None

    raw_position = target_ns.get("evaluatedPosition") or target_player.positionCode or ""
    target_primary_pos = extract_primary_position(raw_position)
    if not target_primary_pos:
        return None

    target_vector = build_radar_vector(target_radar)

    # ══════════════════════════════════════════════════════════════
    # PHASE 1: STRICT POSITION PRE-FILTER
    # Only keep players with the EXACT same primary position.
    # ══════════════════════════════════════════════════════════════
    all_rows = db.query(Player, PlayerStats).join(
        PlayerStats, Player.wyId == PlayerStats.wyId
    ).filter(Player.wyId != target_player.wyId).all()

    current_year = datetime.datetime.now().year
    same_position_players = []

    for p, s in all_rows:
        if not s.normalized_stats:
            continue
        ns = json.loads(s.normalized_stats)
        candidate_pos_raw = ns.get("evaluatedPosition") or p.positionCode or ""
        candidate_primary = extract_primary_position(candidate_pos_raw)

        if candidate_primary != target_primary_pos:
            continue  # STRICT: drop immediately

        c_radar = ns.get("radarScores", {})
        if not c_radar or len(c_radar) < 4:
            continue

        age = 25
        if p.birthDate:
            try:
                age = current_year - int(p.birthDate.split('-')[0])
            except (ValueError, IndexError):
                pass

        same_position_players.append({
            "player": p,
            "radar": c_radar,
            "age": age,
            "position_raw": candidate_pos_raw,
        })

    if not same_position_players:
        return None

    # ══════════════════════════════════════════════════════════════
    # PHASE 2: COSINE SIMILARITY (scipy)
    # Pure math — no LLM, no heuristics, no age bias.
    # ══════════════════════════════════════════════════════════════
    for candidate in same_position_players:
        c_vector = build_radar_vector(candidate["radar"])
        # scipy cosine returns DISTANCE (0 = identical, 2 = opposite)
        # Convert to similarity percentage: (1 - distance) * 100
        distance = cosine_distance(target_vector, c_vector)
        candidate["cosine_similarity"] = round((1.0 - distance) * 100, 2)

    # Sort by cosine similarity, highest first
    same_position_players.sort(key=lambda x: x["cosine_similarity"], reverse=True)
    top_3 = same_position_players[:3]

    if not top_3:
        return None

    # ══════════════════════════════════════════════════════════════
    # PHASE 3: LLM SUMMARIZATION (formatting only, NOT searching)
    # The math has already decided who the twins are.
    # The LLM only writes a 1-sentence human explanation.
    # ══════════════════════════════════════════════════════════════
    target_name = f"{target_player.firstName} {target_player.lastName}".strip() or target_player.shortName

    # Build deterministic fallback explanations first
    explanations = []
    for c in top_3:
        # Find which stats are closest to the target
        matching_traits = []
        for k in VECTOR_KEYS:
            diff = abs(target_radar.get(k, 50) - c["radar"].get(k, 50))
            if diff <= 5:
                matching_traits.append(k)
        best_trait = max(c["radar"].items(), key=lambda x: x[1])[0]
        if matching_traits:
            traits_str = ", ".join(matching_traits[:3])
            explanations.append(
                f"Similaritate cosinus {c['cosine_similarity']}% — profil aproape identic la {traits_str}."
            )
        else:
            explanations.append(
                f"Similaritate cosinus {c['cosine_similarity']}% — cel mai puternic atribut: {best_trait}."
            )

    # Try LLM for nicer prose (strict summarization only)
    try:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash')

            # Build a strict, data-only prompt
            twin_data = []
            for c in top_3:
                twin_data.append({
                    "name": f"{c['player'].firstName} {c['player'].lastName}".strip(),
                    "age": c["age"],
                    "cosine_similarity": c["cosine_similarity"],
                    "stats": {k: c["radar"].get(k, 50) for k in VECTOR_KEYS}
                })

            prompt = (
                f"You are a football scouting assistant. I have already found the 3 most "
                f"statistically similar players to {target_name} (position: {target_primary_pos}) "
                f"using cosine similarity on their performance vectors.\n\n"
                f"Target player stats: {json.dumps({k: target_radar.get(k, 50) for k in VECTOR_KEYS})}\n\n"
                f"Top 3 twins (already selected by math, DO NOT change them):\n"
                f"{json.dumps(twin_data, indent=2)}\n\n"
                f"Based ONLY on the provided JSON data, write exactly 1 sentence per player "
                f"explaining why their stats make them a good twin. "
                f"Return a strict JSON array of exactly 3 strings. No markdown, no extra text."
            )

            resp = model.generate_content(prompt)
            text = resp.text.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            parsed = json.loads(text)
            if isinstance(parsed, list) and len(parsed) == 3:
                explanations = parsed
    except Exception as e:
        print(f"[ai_engine] LLM twin summarization error (using fallback): {e}")

    # ══════════════════════════════════════════════════════════════
    # BUILD RESPONSE
    # ══════════════════════════════════════════════════════════════
    from csv_lookup import player_match_optimizer
    twins_list = []
    for i, c in enumerate(top_3):
        p = c["player"]
        name = f"{p.firstName} {p.lastName}".strip() or p.shortName
        csv_res = player_match_optimizer(p.firstName or '', p.lastName or '')
        photo = csv_res.get('image_url')

        twins_list.append({
            "id": p.wyId,
            "name": name,
            "age": c["age"],
            "position": target_primary_pos,
            "similarityScore": min(c["cosine_similarity"], 99.9),
            "explanation": explanations[i],
            "photoUrl": photo,
            "radarScores": c["radar"],
        })

    return {
        "targetPlayerName": target_name,
        "twins": twins_list,
    }
