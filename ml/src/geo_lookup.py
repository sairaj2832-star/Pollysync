"""
geo_lookup.py
Resolves lat/lon (from backend/frontend map tap) to an Indian state name,
needed for the pollinator proxy table and GBIF region lookups.

For demo/hackathon purposes, DEMO_LOCATIONS gives fixed coordinates per crop
so you don't depend on a live geocoding API call during your demo. The real
reverse_geocode() function is provided for when you wire up live farmer input.
"""

import requests

# Fixed demo coordinates — use these for your test/demo run
DEMO_LOCATIONS = {
    "sunflower": {"lat": 19.99, "lon": 73.78, "region": "Maharashtra"},  # Nashik belt
    "mustard":   {"lat": 26.91, "lon": 75.78, "region": "Rajasthan"},    # Jaipur belt
}


def reverse_geocode(lat: float, lon: float, fallback_region: str = "Maharashtra") -> str:
    """
    Live reverse geocoding via OpenStreetMap Nominatim (free, no API key).
    Returns the Indian state name. Falls back to fallback_region on failure
    or rate-limit — Nominatim allows ~1 request/sec, no bulk use.
    """
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {"lat": lat, "lon": lon, "format": "json"}
    headers = {"User-Agent": "PolliSync-Hackathon/1.0"}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        state = data.get("address", {}).get("state")
        return state if state else fallback_region
    except Exception as e:
        print(f"Reverse geocode failed ({e}), using fallback region: {fallback_region}")
        return fallback_region


if __name__ == "__main__":
    for crop, loc in DEMO_LOCATIONS.items():
        region = reverse_geocode(loc["lat"], loc["lon"])
        print(f"{crop}: lat={loc['lat']}, lon={loc['lon']} -> region={region}")