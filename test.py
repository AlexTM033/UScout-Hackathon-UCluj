import os
import sys

# Ensure database is initialized
from database import init_db, SessionLocal, Player, PlayerStats
init_db()

print("Database initialized.")

from ingestion import run_ingestion

db = SessionLocal()
try:
    print("Running ingestion...")
    run_ingestion(db)
    
    players = db.query(Player).all()
    print(f"Total players in DB: {len(players)}")
    
    stats = db.query(PlayerStats).all()
    print(f"Total players with stats (>=450 mins): {len(stats)}")
    
    # Check top 5 by score
    top_players = db.query(Player, PlayerStats).join(PlayerStats, Player.wyId == PlayerStats.wyId).order_by(PlayerStats.performance_score.desc()).limit(5).all()
    print("\\nTop 5 Players by Score:")
    for p, s in top_players:
        output_str = f"{p.firstName} {p.lastName} ({p.positionCode}): {s.performance_score} (Mins: {s.minutesOnField})"
        print(output_str.encode('ascii', 'replace').decode('ascii'))
finally:
    db.close()
