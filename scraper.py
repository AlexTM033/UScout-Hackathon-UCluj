import httpx
import re
import time
from typing import Optional

# Local Dictionary Cache with TTL (MODULE 3)
LOCAL_CACHE = {}
TTL_SECONDS = 7 * 24 * 60 * 60 # 7 days

async def get_market_value(player_name: str, wyId: int) -> Optional[int]:
    # Check cache first
    now = time.time()
    if wyId in LOCAL_CACHE:
        cached_val, timestamp = LOCAL_CACHE[wyId]
        if (now - timestamp) < TTL_SECONDS:
            return cached_val
            
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Step 1: Search for player
            search_url = f"https://transfermarkt-api.fly.dev/players/search/{player_name}"
            search_resp = await client.get(search_url)
            
            if search_resp.status_code != 200:
                return None
                
            search_data = search_resp.json()
            results = search_data.get("results", [])
            
            if not results:
                return None
                
            # Step 2: Get market value directly from search results
            best_match = results[0]
            value_str = best_match.get("marketValue")
            
            parsed_value = parse_market_value(value_str)
            
            # Save to local cache
            if parsed_value is not None:
                LOCAL_CACHE[wyId] = (parsed_value, now)
            
            return parsed_value
            
    except Exception as e:
        import traceback
        print(f"Error fetching external transfermarkt API for {player_name}: {e}\n{traceback.format_exc()}")
        return None

def parse_market_value(value_str) -> Optional[int]:
    # Check if the API already returned a clean integer or float
    if isinstance(value_str, (int, float)):
        return int(value_str)
        
    # e.g., "€1.50m" -> 1500000, "€800k" -> 800000, "-" -> null
    if not value_str or not isinstance(value_str, str) or value_str == "-" or value_str == "Not available":
        return None
        
    value_str = value_str.lower().replace('€', '').replace(',', '.').strip()
    
    multiplier = 1
    if 'm' in value_str:
        multiplier = 1000000
        value_str = value_str.replace('m', '')
    elif 'k' in value_str:
        multiplier = 1000
        value_str = value_str.replace('k', '')
        
    try:
        # Strip any remaining non-numeric characters (except dot) just in case
        cleaned_num = re.sub(r'[^\d.]', '', value_str)
        if not cleaned_num:
            return None
        return int(float(cleaned_num) * multiplier)
    except ValueError:
        return None
