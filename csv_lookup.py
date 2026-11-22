"""
CSV-based Transfermarkt data lookup engine.
Loads players.csv (and optionally player_valuations.csv) from ./transfermarkt-datasets/
and provides robust name matching with diacritics normalization.

Public API:
    player_match_optimizer(first_name, last_name) -> dict
"""
import csv
import re
import os
import unicodedata
from typing import Optional, Dict

# --- In-memory indexes (lazy-loaded once) ---
_players_index: Optional[Dict] = None          # normalized_name -> row dict
_latest_valuations: Optional[Dict] = None       # player_id -> latest market value

DATASETS_DIR = os.path.join(os.path.dirname(__file__), "transfermarkt-datasets")
PLAYERS_CSV = os.path.join(DATASETS_DIR, "players.csv")
VALUATIONS_CSV = os.path.join(DATASETS_DIR, "player_valuations.csv")


# ──────────────────────── String normalisation ────────────────────────

def _strip_diacritics(text: str) -> str:
    """Remove all Unicode diacritics/accents (ă→a, ș→s, ț→t, â→a, î→i, etc.)."""
    nfkd = unicodedata.normalize('NFD', text)
    return ''.join(c for c in nfkd if unicodedata.category(c) != 'Mn')


def _normalize(name: str) -> str:
    """Lowercase, strip diacritics, remove non-alpha chars except spaces."""
    name = _strip_diacritics(name.lower().strip())
    name = re.sub(r'[^a-z\s]', '', name)
    return ' '.join(name.split())  # collapse whitespace


# ──────────────────────── CSV loaders ─────────────────────────────────

def _load_players_index() -> Dict:
    """
    Build an in-memory index from transfermarkt-datasets/players.csv.
    Keys: normalised variants of the player name.
    Value: dict with player_id, image_url, market_value_in_eur, name, club, etc.

    Columns used from players.csv:
        player_id, first_name, last_name, name, image_url,
        market_value_in_eur, current_club_name
    """
    global _players_index
    if _players_index is not None:
        return _players_index

    _players_index = {}
    if not os.path.exists(PLAYERS_CSV):
        print(f"[csv_lookup] WARNING: players.csv not found at {PLAYERS_CSV}")
        return _players_index

    with open(PLAYERS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            pid = row.get('player_id', '').strip()
            csv_name = (row.get('name') or '').strip()           # e.g. "Miroslav Klose"
            csv_first = (row.get('first_name') or '').strip()
            csv_last = (row.get('last_name') or '').strip()
            image_url = (row.get('image_url') or '').strip()
            club = (row.get('current_club_name') or '').strip()
            nationality = (row.get('country_of_citizenship') or '').strip()
            height_raw = (row.get('height_in_cm') or '').strip()
            foot = (row.get('foot') or '').strip()

            # Parse market value
            raw_val = row.get('market_value_in_eur', '') or ''
            try:
                market_value = float(raw_val) if raw_val else None
            except (ValueError, TypeError):
                market_value = None

            # Parse height
            try:
                height_cm = int(float(height_raw)) if height_raw else None
            except (ValueError, TypeError):
                height_cm = None

            contract_expiration = (row.get('contract_expiration_date') or '').strip()

            entry = {
                'player_id': pid,
                'name': csv_name,
                'first_name': csv_first,
                'last_name': csv_last,
                'image_url': image_url if image_url else None,
                'market_value_in_eur': market_value,
                'club': club,
                'nationality': nationality or None,
                'height_cm': height_cm,
                'foot': foot.capitalize() if foot else None,
                'contract_expiration': contract_expiration or None,
            }

            # Index by normalised "name" column (primary key for lookup)
            norm_name = _normalize(csv_name)
            if norm_name and norm_name not in _players_index:
                _players_index[norm_name] = entry

            # Also index by "first_name last_name"
            full_name = f"{csv_first} {csv_last}".strip()
            norm_full = _normalize(full_name)
            if norm_full and norm_full != norm_name and norm_full not in _players_index:
                _players_index[norm_full] = entry

            # Also index by "last_name first_name" (reversed order)
            reversed_name = f"{csv_last} {csv_first}".strip()
            norm_reversed = _normalize(reversed_name)
            if norm_reversed and norm_reversed != norm_name and norm_reversed != norm_full and norm_reversed not in _players_index:
                _players_index[norm_reversed] = entry

    print(f"[csv_lookup] Indexed {len(_players_index)} name entries from players.csv.")
    return _players_index


def _load_latest_valuations() -> Dict:
    """
    Load player_valuations.csv and keep only the most recent valuation per player.
    Returns: player_id -> market_value_in_eur (float)
    """
    global _latest_valuations
    if _latest_valuations is not None:
        return _latest_valuations

    _latest_valuations = {}
    if not os.path.exists(VALUATIONS_CSV):
        print(f"[csv_lookup] INFO: player_valuations.csv not found — using players.csv values only.")
        return _latest_valuations

    # Track the latest date per player
    latest_dates: Dict[str, str] = {}

    with open(VALUATIONS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            pid = row.get('player_id', '').strip()
            date = row.get('date', '').strip()
            try:
                val = float(row.get('market_value_in_eur', 0) or 0)
            except (ValueError, TypeError):
                val = 0.0

            if not pid or val <= 0:
                continue

            # Keep the entry with the latest date
            if pid not in latest_dates or date > latest_dates[pid]:
                latest_dates[pid] = date
                _latest_valuations[pid] = val

    print(f"[csv_lookup] Loaded {len(_latest_valuations)} latest valuations from player_valuations.csv.")
    return _latest_valuations


# ──────────────────────── Value formatting ────────────────────────────

def _format_market_value(value_eur: float) -> str:
    """Convert raw EUR integer to readable string: 1500000 -> '€1.50m', 250000 -> '€250k'."""
    if value_eur >= 1_000_000:
        return f"€{value_eur / 1_000_000:.2f}m"
    elif value_eur >= 1_000:
        return f"€{value_eur / 1_000:.0f}k"
    elif value_eur > 0:
        return f"€{int(value_eur)}"
    return None


# ──────────────────────── Main lookup ─────────────────────────────────

def player_match_optimizer(first_name: str, last_name: str) -> Dict:
    """
    Main lookup function.  Receives internal DB player's first/last name.
    Returns dict with:
      - found: bool
      - image_url: str or None
      - market_value_raw: float or None
      - market_value_formatted: str or None (e.g. '€1.50m')
      - tm_name: str
      - tm_club: str
    """
    players = _load_players_index()
    valuations = _load_latest_valuations()

    full_name = f"{first_name} {last_name}".strip()
    search_norm = _normalize(full_name)

    if not search_norm:
        return _empty_result()

    # Strategy 1: Exact normalised match
    match = players.get(search_norm)

    # Strategy 2: Try reversed name order
    if not match:
        reversed_norm = _normalize(f"{last_name} {first_name}".strip())
        match = players.get(reversed_norm)

    # Strategy 3: Try last name only (common for single-name players like "Neymar")
    if not match and last_name:
        match = players.get(_normalize(last_name))

    # Strategy 4: Fuzzy substring — find keys where ALL search words appear
    if not match:
        search_parts = search_norm.split()
        if len(search_parts) >= 2:
            candidates = []
            for key, entry in players.items():
                if all(part in key for part in search_parts):
                    candidates.append((key, entry))

            if len(candidates) == 1:
                match = candidates[0][1]
            elif len(candidates) > 1:
                # Pick the shortest key (most specific match)
                candidates.sort(key=lambda x: len(x[0]))
                match = candidates[0][1]

    # Strategy 5: Reverse containment — CSV key words all appear in the search term
    # Handles "Daniel Nistor" (DB) matching "Dan Nistor" (CSV) since "dan" is in "daniel"
    if not match:
        search_parts = search_norm.split()
        candidates = []
        for key, entry in players.items():
            key_parts = key.split()
            if len(key_parts) >= 2 and all(
                any(kp in sp for sp in search_parts) for kp in key_parts
            ):
                # Score by how many key parts match exactly vs. partially
                exact = sum(1 for kp in key_parts if kp in search_parts)
                candidates.append((exact, len(key), key, entry))

        if candidates:
            # Sort by most exact matches first, then shortest key
            candidates.sort(key=lambda x: (-x[0], x[1]))
            match = candidates[0][3]

    if not match:
        return _empty_result()

    # --- Resolve market value ---
    pid = match['player_id']
    # Prefer the valuation from player_valuations.csv (more up-to-date)
    raw_value = valuations.get(pid) or match.get('market_value_in_eur')
    formatted_value = _format_market_value(raw_value) if raw_value else None

    # --- Validate image URL ---
    image_url = match.get('image_url')
    if image_url and ('default.jpg' in image_url or 'default' in image_url.lower()):
        image_url = None  # Treat TM default placeholder as no image

    return {
        'found': True,
        'player_id': pid,
        'image_url': image_url,
        'market_value_raw': raw_value,
        'market_value_formatted': formatted_value,
        'tm_name': match.get('name', ''),
        'tm_club': match.get('club', ''),
        'nationality': match.get('nationality'),
        'height_cm': match.get('height_cm'),
        'foot': match.get('foot'),
        'contract_expiration': match.get('contract_expiration'),
    }


def get_height_index() -> Dict:
    """
    Returns {normalized_name: height_cm} for all players in the CSV.
    Used by the scoring engine for Physicality contextual modifiers.
    """
    players = _load_players_index()
    height_map = {}
    seen_ids = set()
    
    for norm_name, entry in players.items():
        pid = entry.get('player_id')
        if pid in seen_ids:
            continue
        seen_ids.add(pid)
        
        h = entry.get('height_cm')
        if h and h > 0:
            # Index by the CSV name (normalized)
            csv_name = entry.get('name', '')
            if csv_name:
                height_map[_normalize(csv_name)] = h
            # Also index by first+last
            fl = f"{entry.get('first_name', '')} {entry.get('last_name', '')}".strip()
            if fl:
                height_map[_normalize(fl)] = h
    
    return height_map


def _empty_result() -> Dict:
    return {
        'found': False,
        'image_url': None,
        'market_value_raw': None,
        'market_value_formatted': None,
        'tm_name': '',
        'tm_club': '',
        'nationality': None,
        'height_cm': None,
        'foot': None,
    }

def get_transfer_history(player_id: str) -> list:
    """Load transfers for a specific TM player_id."""
    if not player_id or not os.path.exists(TRANSFERS_CSV):
        return []
    
    transfers = []
    with open(TRANSFERS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('player_id') == str(player_id):
                fee_raw = row.get('transfer_fee', '0')
                try:
                    fee_val = float(fee_raw)
                except:
                    fee_val = 0
                
                if fee_val > 0:
                    transfer_type = f"{_format_market_value(fee_val)}" if fee_val > 1000 else f"€{int(fee_val)}"
                else:
                    transfer_type = "Împrumut / Liber"
                
                mv_raw = row.get('market_value_in_eur', '0')
                try:
                    mv_float = float(mv_raw)
                    mv = _format_market_value(mv_float) if mv_float > 0 else "-"
                except:
                    mv = "-"
                
                transfers.append({
                    'date': row.get('transfer_date'),
                    'season': row.get('transfer_season', '-'),
                    'from_club_name': row.get('from_club_name', 'N/A'),
                    'to_club_name': row.get('to_club_name', 'N/A'),
                    'transfer_type': transfer_type,
                    'market_value': mv,
                    'fee': fee_raw,
                })
    
    # Sort by date descending (newest first)
    transfers.sort(key=lambda x: x['date'] or '', reverse=True)
    return transfers

TRANSFERS_CSV = os.path.join(DATASETS_DIR, "transfers.csv")
