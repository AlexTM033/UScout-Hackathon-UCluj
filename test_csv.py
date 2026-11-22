import csv, sys, unicodedata, re
sys.stdout.reconfigure(encoding='utf-8')

def strip_acc(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

def clean_name(raw):
    """Remove trailing (ID) from player_name like 'Tommaso Nistor (1001920)' -> 'Tommaso Nistor'"""
    return re.sub(r'\s*\(\d+\)\s*$', '', raw).strip()

targets = ['mark tutu', 'dan nistor', 'cristian sima', 'eddy gnahore']
r = csv.DictReader(open(r'c:\Users\gabi2\Desktop\Hack1\transfermarkt\player_profiles\player_profiles.csv', 'r', encoding='utf-8'))

found = {}
for row in r:
    raw_name = row['player_name']
    cleaned = clean_name(raw_name)
    name_norm = strip_acc(cleaned).lower()
    home_name = strip_acc(row.get('name_in_home_country', '') or '').lower()
    
    for t in targets:
        parts = t.split()
        if all(p in name_norm for p in parts) or all(p in home_name for p in parts):
            if t not in found:
                found[t] = []
            found[t].append({
                'id': row['player_id'],
                'raw_name': raw_name,
                'cleaned': cleaned,
                'home_name': row.get('name_in_home_country', ''),
                'img': row['player_image_url'][:100],
                'club': row.get('current_club_name', '')
            })

for t, matches in found.items():
    print(f"\n=== '{t}' ===")
    for m in matches:
        print(f"  id={m['id']}, name='{m['cleaned']}', home='{m['home_name']}', club={m['club']}, img={m['img']}")

# Check how many unique player_ids have market values
print("\n--- Total players with market values ---")
mv = csv.DictReader(open(r'c:\Users\gabi2\Desktop\Hack1\transfermarkt\player_latest_market_value\player_latest_market_value.csv', 'r', encoding='utf-8'))
mv_count = 0
sample_vals = []
for i, row in enumerate(mv):
    mv_count += 1
    if float(row['value']) > 0 and len(sample_vals) < 5:
        sample_vals.append(row)
print(f"Total: {mv_count}")
print("Samples with value > 0:")
for s in sample_vals:
    print(f"  id={s['player_id']}, value={s['value']}")
