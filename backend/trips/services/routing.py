import requests
import polyline

OSRM_URL = "https://router.project-osrm.org"
KM_TO_MILES = 0.621371


def get_route(
    origin: tuple[float, float],
    destination: tuple[float, float],
    waypoints: list[tuple[float, float]] | None = None,
) -> dict:
    """
    Get driving route from OSRM.
    Coordinates are (lat, lon) tuples.
    Returns route with distance, duration, and geometry.
    """
    # OSRM expects lon,lat order
    coords = [f"{origin[1]},{origin[0]}"]
    if waypoints:
        for wp in waypoints:
            coords.append(f"{wp[1]},{wp[0]}")
    coords.append(f"{destination[1]},{destination[0]}")

    coords_str = ";".join(coords)

    response = requests.get(
        f"{OSRM_URL}/route/v1/driving/{coords_str}",
        params={
            "overview": "full",
            "geometries": "polyline",
            "steps": "true",
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()

    if data.get("code") != "Ok" or not data.get("routes"):
        raise ValueError("Could not calculate route between the given locations")

    route = data["routes"][0]
    geometry = polyline.decode(route["geometry"])

    total_distance_km = route["distance"] / 1000
    total_distance_miles = total_distance_km * KM_TO_MILES
    total_duration_hours = route["duration"] / 3600

    # Extract leg distances for multi-stop routes
    legs = []
    for leg in route["legs"]:
        legs.append({
            "distance_miles": (leg["distance"] / 1000) * KM_TO_MILES,
            "duration_hours": leg["duration"] / 3600,
        })

    return {
        "total_distance_miles": round(total_distance_miles, 1),
        "total_duration_hours": round(total_duration_hours, 2),
        "geometry": geometry,
        "legs": legs,
    }


def get_point_along_route(
    geometry: list[tuple[float, float]],
    target_miles: float,
) -> tuple[float, float] | None:
    """
    Find the approximate lat/lon point along a route geometry
    at a given distance in miles from the start.
    Uses the Haversine formula for segment distances.
    """
    import math

    accumulated = 0.0
    target_km = target_miles / KM_TO_MILES

    for i in range(len(geometry) - 1):
        lat1, lon1 = math.radians(geometry[i][0]), math.radians(geometry[i][1])
        lat2, lon2 = math.radians(geometry[i + 1][0]), math.radians(geometry[i + 1][1])

        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))
        segment_km = 6371 * c

        if accumulated + segment_km >= target_km:
            return geometry[i + 1]

        accumulated += segment_km

    return geometry[-1] if geometry else None
