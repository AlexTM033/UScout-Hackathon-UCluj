from ingestion import build_position_ledger
from database import SessionLocal, Player

db = SessionLocal()
ledger, _ = build_position_ledger('./Date - meciuri')

# Check Olaru
p = db.query(Player).filter(Player.shortName.like('%Olaru%')).first()
pos = ledger.get(p.wyId, {})
total = sum(v['minutes'] for v in pos.values())

print(f"\n{p.shortName} — Total: {total:.0f} min across {len(pos)} raw positions")
print(f"{'Position':>30} {'Minutes':>8} {'Weight':>8} {'Status':>8}")
print("-" * 60)

for code, v in sorted(pos.items(), key=lambda x: x[1]['minutes'], reverse=True):
    weight = (v['minutes'] / total) * 100
    status = "KEEP" if weight >= 10 else "NOISE"
    print(f"{v['name'] + ' (' + code + ')':>30} {v['minutes']:>7.0f}m {weight:>6.1f}% {status:>8}")

print(f"\nRule of Three applied: max 3 survive (1 primary + 2 secondary)")
