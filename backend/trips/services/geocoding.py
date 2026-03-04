import requests

NOMINATIM_URL = "https://nominatim.openstreetmap.org"
HEADERS = {"User-Agent": "SpotterTripPlanner/1.0 (github.com/JobDelToro/spotter-trip)"}


def search_locations(query: str, limit: int = 5) -> list[dict]:
    """Search for locations using Nominatim geocoding API."""
    response = requests.get(
        f"{NOMINATIM_URL}/search",
        params={
            "q": query,
            "format": "json",
            "limit": limit,
            "countrycodes": "us",
        },
        headers=HEADERS,
        timeout=10,
    )
    response.raise_for_status()
    return [
        {
            "display_name": r["display_name"],
            "lat": float(r["lat"]),
            "lon": float(r["lon"]),
        }
        for r in response.json()
    ]
