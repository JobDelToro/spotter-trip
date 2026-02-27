from django.urls import path
from trips.views import PlanTripView, LocationSearchView

urlpatterns = [
    path("trip/plan", PlanTripView.as_view(), name="plan-trip"),
    path("locations/search", LocationSearchView.as_view(), name="location-search"),
]
