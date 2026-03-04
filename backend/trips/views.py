from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from trips.serializers import TripRequestSerializer
from trips.services.geocoding import search_locations
from trips.services.routing import get_route, get_point_along_route
from trips.services.hos import calculate_trip_plan
from trips.services.eld import generate_eld_logs


def parse_coords(value: str) -> tuple[float, float]:
    """Parse 'lat,lon' string into a tuple."""
    lat, lon = value.split(",")
    return float(lat), float(lon)


class PlanTripView(APIView):
    """Plan a trip with HOS-compliant route and ELD logs."""

    def post(self, request):
        serializer = TripRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        try:
            current = parse_coords(data["current_location"])
            pickup = parse_coords(data["pickup_location"])
            dropoff = parse_coords(data["dropoff_location"])
        except (ValueError, IndexError):
            return Response(
                {"detail": "Invalid coordinate format. Expected 'lat,lon'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            route = get_route(current, dropoff, waypoints=[pickup])
        except Exception as e:
            return Response(
                {"detail": f"Routing error: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        cycle_hours = data.get("current_cycle_hours", 0)

        try:
            plan = calculate_trip_plan(route["legs"], cycle_hours)
        except Exception as e:
            return Response(
                {"detail": f"HOS calculation error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Add lat/lon to each stop using route geometry
        for stop in plan["stops"]:
            point = get_point_along_route(
                route["geometry"], stop.get("mile_marker", 0)
            )
            if point:
                stop["location"] = {"lat": point[0], "lon": point[1]}

        eld_logs = generate_eld_logs(plan["timeline"])

        return Response({
            "route": {
                "total_distance_miles": route["total_distance_miles"],
                "total_duration_hours": route["total_duration_hours"],
                "geometry": route["geometry"],
                "legs": route["legs"],
            },
            "stops": plan["stops"],
            "eld_logs": eld_logs,
            "summary": plan["summary"],
        })


class LocationSearchView(APIView):
    """Search for locations using geocoding."""

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        if len(query) < 3:
            return Response([])

        try:
            results = search_locations(query)
        except Exception as e:
            return Response(
                {"detail": f"Geocoding error: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(results)
