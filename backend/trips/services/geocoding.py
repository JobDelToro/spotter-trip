import requests

PHOTON_URL = "https://photon.komoot.io/api"
HEADERS = {"User-Agent": "SpotterTripPlanner/1.0 (github.com/JobDelToro/spotter-trip)"}


def search_locations(query: str, limit: int = 5) -> list[dict]:
    """Search for US locations using Photon geocoding API."""
    response = requests.get(
        PHOTON_URL,
        params={"q": query, "limit": limit * 2, "lang": "en"},
        headers=HEADERS,
        timeout=10,
    )
    response.raise_for_status()

    results = []
    for feature in response.json().get("features", []):
        props = feature.get("properties", {})
        if props.get("country") not in ("United States of America", "United States"):
            continue
        coords = feature["geometry"]["coordinates"]  # [lon, lat]
        parts = [p for p in [
            props.get("name"),
            props.get("city") if props.get("name") != props.get("city") else None,
            props.get("state"),
            "USA",
        ] if p]
        results.append({
            "display_name": ", ".join(parts),
            "lat": coords[1],
            "lon": coords[0],
        })
        if len(results) >= limit:
            break

    return results
