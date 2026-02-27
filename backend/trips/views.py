from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from trips.serializers import TripRequestSerializer
from trips.services.geocoding import search_locations


class PlanTripView(APIView):
    """Plan a trip with HOS-compliant route and ELD logs."""

    def post(self, request):
        serializer = TripRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # TODO: implement in next commits
        return Response({"message": "Trip planning coming soon"})


class LocationSearchView(APIView):
    """Search for locations using geocoding."""

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        if len(query) < 3:
            return Response([])

        results = search_locations(query)
        return Response(results)
