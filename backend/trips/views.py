from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from trips.serializers import TripRequestSerializer
from trips.services.geocoding import search_locations
from trips.services.routing import get_route


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

        # TODO: HOS calculation and ELD log generation in next commits
        return Response({
            "route": {
                "total_distance_miles": route["total_distance_miles"],
                "total_duration_hours": route["total_duration_hours"],
                "geometry": route["geometry"],
                "legs": route["legs"],
            },
            "stops": [],
            "eld_logs": [],
        })


class LocationSearchView(APIView):
    """Search for locations using geocoding."""

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        if len(query) < 3:
            return Response([])

        results = search_locations(query)
        return Response(results)
