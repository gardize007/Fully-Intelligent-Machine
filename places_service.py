from builtins import Exception, float, str
import requests
from urllib.parse import urlencode
from typing import Dict, List

OSM_NOMINATE_URL = "https://nominatim.openstreetmap.org/search"

HEADERS = {
    # Use a descriptive UA per Nominate usage policy
    "User-Agent": "YourIntelligentMachine/1.0 (contact: example@example.com)"
}

def osm_search(query: str, near: str | None, limit: int = 5) -> List[Dict]:
    q = f"{query} {near}" if near else query
    params = {
        "q": q,
        "format": "json",
        "addressdetails": 1,
        "limit": limit
    }
    resp = requests.get(OSM_NOMINATE_URL, params=params, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    results = []
    for item in data:
        addr = item.get("display_name", "")
        results.append({
            "name": item.get("namedetails", {}).get("name", item.get("display_name", "").split(",")[0]),
            "address": addr,
            "lat": float(item.get("lat")),
            "lon": float(item.get("lon")),
            "rating": None,          # OSM doesn't provide ratings
            "open_now": None,        # OSM doesn't provide open_now
            "provider": "openstreetmap"
        })
    return results

def parse_places_query(text: str) -> Dict:
    t = text.lower()
    # naive parse: try to split by " in " or " near "
    near = None
    if " near " in t:
        parts = t.split(" near ", 1)
        query = parts[0].replace("find", "").replace("show", "").strip()
        near = parts[1].strip()
    elif " in " in t:
        parts = t.split(" in ", 1)
        query = parts[0].replace("find", "").replace("show", "").strip()
        near = parts[1].strip()
    else:
        query = t.replace("find", "").replace("show", "").strip()
    # clean generic words
    for w in ["me", "nearest", "closest"]:
        query = query.replace(w, "").strip()
    return {"query": query, "near": near}

class PlacesService:
    def search_from_text(self, text: str) -> Dict:
        try:
            parsed = parse_places_query(text)
            query = parsed["query"]
            near = parsed["near"]
            if not query:
                return {"results": [], "attribution": ["OpenStreetMap"], "error": "Could not parse place type."}
            results = osm_search(query=query, near=near, limit=5)
            return {"results": results, "attribution": ["OpenStreetMap"]}
        except requests.HTTPError as e:
            return {"results": [], "attribution": ["OpenStreetMap"], "error": f"HTTP error: {e}"}
        except Exception as e:
            return {"results": [], "attribution": ["OpenStreetMap"], "error": str(e)}
