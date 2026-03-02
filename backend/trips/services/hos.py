from datetime import datetime, timedelta

# FMCSA HOS limits for property-carrying vehicles
MAX_DRIVING_HOURS = 11.0
MAX_DUTY_WINDOW_HOURS = 14.0
BREAK_AFTER_DRIVING_HOURS = 8.0
BREAK_DURATION_HOURS = 0.5
OFF_DUTY_RESET_HOURS = 10.0
MAX_CYCLE_HOURS = 70.0

# Trip assumptions
FUEL_STOP_INTERVAL_MILES = 1000
FUEL_STOP_DURATION_HOURS = 0.5
PICKUP_DURATION_HOURS = 1.0
DROPOFF_DURATION_HOURS = 1.0
PRE_TRIP_INSPECTION_HOURS = 0.25


def calculate_trip_plan(
    legs: list[dict],
    current_cycle_hours: float,
    start_time: datetime | None = None,
) -> dict:
    """
    Calculate an HOS-compliant trip plan given route legs.

    Each leg has: distance_miles, duration_hours
    Leg 0: current_location -> pickup
    Leg 1: pickup -> dropoff

    Returns stops list and timeline of duty status changes.
    """
    if start_time is None:
        start_time = datetime.now().replace(minute=0, second=0, microsecond=0)

    state = DriverState(
        current_time=start_time,
        cycle_hours_used=current_cycle_hours,
    )

    timeline = []
    stops = []

    # Pre-trip inspection
    state.add_on_duty(
        PRE_TRIP_INSPECTION_HOURS, "Pre-trip inspection", timeline
    )

    # Leg 0: drive to pickup
    _drive_leg(state, legs[0], timeline, stops, leg_index=0)

    # Pickup stop
    pickup_stop = {
        "type": "pickup",
        "duration_hours": PICKUP_DURATION_HOURS,
        "start_time": state.current_time.isoformat(),
        "mile_marker": legs[0]["distance_miles"],
    }
    state.add_on_duty(PICKUP_DURATION_HOURS, "Pickup", timeline)
    pickup_stop["end_time"] = state.current_time.isoformat()
    stops.append(pickup_stop)

    # Leg 1: drive to dropoff
    _drive_leg(
        state,
        legs[1],
        timeline,
        stops,
        leg_index=1,
        mile_offset=legs[0]["distance_miles"],
    )

    # Dropoff stop
    dropoff_stop = {
        "type": "dropoff",
        "duration_hours": DROPOFF_DURATION_HOURS,
        "start_time": state.current_time.isoformat(),
        "mile_marker": legs[0]["distance_miles"] + legs[1]["distance_miles"],
    }
    state.add_on_duty(DROPOFF_DURATION_HOURS, "Drop-off", timeline)
    dropoff_stop["end_time"] = state.current_time.isoformat()
    stops.append(dropoff_stop)

    # Final off-duty
    timeline.append({
        "status": "off_duty",
        "start_time": state.current_time.isoformat(),
        "end_time": (state.current_time + timedelta(hours=2)).isoformat(),
        "duration_hours": 2.0,
        "location": "Final destination",
    })

    total_miles = legs[0]["distance_miles"] + legs[1]["distance_miles"]
    trip_duration = state.current_time - start_time

    return {
        "stops": stops,
        "timeline": timeline,
        "summary": {
            "total_distance_miles": round(total_miles, 1),
            "total_driving_hours": round(state.total_driving_hours, 1),
            "total_trip_hours": round(trip_duration.total_seconds() / 3600, 1),
            "number_of_stops": len(stops),
            "number_of_rest_periods": sum(
                1 for s in stops if s["type"] in ("rest", "overnight")
            ),
        },
    }


class DriverState:
    """Tracks the driver's current HOS state as the trip progresses."""

    def __init__(self, current_time: datetime, cycle_hours_used: float = 0):
        self.current_time = current_time
        self.cycle_hours_used = cycle_hours_used
        self.shift_driving_hours = 0.0
        self.shift_duty_hours = 0.0
        self.driving_since_break = 0.0
        self.total_driving_hours = 0.0

    @property
    def remaining_driving(self) -> float:
        """Hours of driving left in current shift."""
        by_driving_limit = MAX_DRIVING_HOURS - self.shift_driving_hours
        by_window = MAX_DUTY_WINDOW_HOURS - self.shift_duty_hours
        by_cycle = MAX_CYCLE_HOURS - self.cycle_hours_used
        return max(0, min(by_driving_limit, by_window, by_cycle))

    @property
    def needs_30min_break(self) -> bool:
        return self.driving_since_break >= BREAK_AFTER_DRIVING_HOURS

    @property
    def hours_until_break(self) -> float:
        return max(0, BREAK_AFTER_DRIVING_HOURS - self.driving_since_break)

    def add_driving(self, hours: float, location: str, timeline: list):
        timeline.append({
            "status": "driving",
            "start_time": self.current_time.isoformat(),
            "end_time": (
                self.current_time + timedelta(hours=hours)
            ).isoformat(),
            "duration_hours": round(hours, 2),
            "location": location,
        })
        self.current_time += timedelta(hours=hours)
        self.shift_driving_hours += hours
        self.shift_duty_hours += hours
        self.driving_since_break += hours
        self.cycle_hours_used += hours
        self.total_driving_hours += hours

    def add_on_duty(self, hours: float, location: str, timeline: list):
        timeline.append({
            "status": "on_duty",
            "start_time": self.current_time.isoformat(),
            "end_time": (
                self.current_time + timedelta(hours=hours)
            ).isoformat(),
            "duration_hours": round(hours, 2),
            "location": location,
        })
        self.current_time += timedelta(hours=hours)
        self.shift_duty_hours += hours
        self.cycle_hours_used += hours

    def add_break(self, timeline: list, location: str = "Rest area"):
        timeline.append({
            "status": "off_duty",
            "start_time": self.current_time.isoformat(),
            "end_time": (
                self.current_time + timedelta(hours=BREAK_DURATION_HOURS)
            ).isoformat(),
            "duration_hours": BREAK_DURATION_HOURS,
            "location": location,
        })
        self.current_time += timedelta(hours=BREAK_DURATION_HOURS)
        self.shift_duty_hours += BREAK_DURATION_HOURS
        self.driving_since_break = 0

    def add_rest(self, timeline: list, location: str = "Rest stop"):
        timeline.append({
            "status": "sleeper_berth",
            "start_time": self.current_time.isoformat(),
            "end_time": (
                self.current_time + timedelta(hours=OFF_DUTY_RESET_HOURS)
            ).isoformat(),
            "duration_hours": OFF_DUTY_RESET_HOURS,
            "location": location,
        })
        self.current_time += timedelta(hours=OFF_DUTY_RESET_HOURS)
        # Reset shift counters after 10-hour rest
        self.shift_driving_hours = 0
        self.shift_duty_hours = 0
        self.driving_since_break = 0


def _drive_leg(
    state: DriverState,
    leg: dict,
    timeline: list,
    stops: list,
    leg_index: int,
    mile_offset: float = 0,
):
    """
    Simulate driving a single leg, inserting mandatory stops as needed.
    """
    remaining_miles = leg["distance_miles"]
    if leg["duration_hours"] > 0:
        avg_speed = leg["distance_miles"] / leg["duration_hours"]
    else:
        avg_speed = 60.0
    miles_since_fuel = 0.0
    leg_miles_driven = 0.0

    while remaining_miles > 0.1:
        # Check if we need a 10-hour rest first
        if state.remaining_driving <= 0:
            stops.append({
                "type": "overnight",
                "duration_hours": OFF_DUTY_RESET_HOURS,
                "start_time": state.current_time.isoformat(),
                "mile_marker": round(mile_offset + leg_miles_driven, 1),
            })
            state.add_rest(timeline, "Overnight rest")
            stops[-1]["end_time"] = state.current_time.isoformat()
            miles_since_fuel = 0

        # Calculate how far we can drive before the next mandatory stop
        hours_available = state.remaining_driving
        hours_until_break = state.hours_until_break

        # Find the next limiting factor
        drive_hours = min(hours_available, hours_until_break)

        # Check fuel stop
        miles_can_drive = drive_hours * avg_speed
        miles_until_fuel = FUEL_STOP_INTERVAL_MILES - miles_since_fuel

        if miles_until_fuel <= 0:
            miles_until_fuel = FUEL_STOP_INTERVAL_MILES

        fuel_stop_needed = False
        if miles_until_fuel < miles_can_drive:
            miles_can_drive = miles_until_fuel
            drive_hours = miles_can_drive / avg_speed
            fuel_stop_needed = True

        # Don't drive more than remaining distance
        if miles_can_drive > remaining_miles:
            miles_can_drive = remaining_miles
            drive_hours = miles_can_drive / avg_speed
            fuel_stop_needed = False

        # Drive this segment
        if drive_hours > 0.01:
            state.add_driving(drive_hours, "En route", timeline)
            remaining_miles -= miles_can_drive
            miles_since_fuel += miles_can_drive
            leg_miles_driven += miles_can_drive

        # Handle fuel stop
        if fuel_stop_needed and remaining_miles > 0.1:
            stop_time = state.current_time.isoformat()
            # Combine fuel stop with 30-min break if break is also due
            if state.needs_30min_break:
                state.add_break(timeline, "Fuel stop & break")
                stops.append({
                    "type": "fuel",
                    "duration_hours": FUEL_STOP_DURATION_HOURS,
                    "start_time": stop_time,
                    "end_time": state.current_time.isoformat(),
                    "mile_marker": round(mile_offset + leg_miles_driven, 1),
                })
            else:
                state.add_on_duty(
                    FUEL_STOP_DURATION_HOURS, "Fuel stop", timeline
                )
                stops.append({
                    "type": "fuel",
                    "duration_hours": FUEL_STOP_DURATION_HOURS,
                    "start_time": stop_time,
                    "end_time": state.current_time.isoformat(),
                    "mile_marker": round(mile_offset + leg_miles_driven, 1),
                })
            miles_since_fuel = 0
            continue

        # Handle 30-minute break (if not already handled with fuel)
        if state.needs_30min_break and remaining_miles > 0.1:
            stop_time = state.current_time.isoformat()
            state.add_break(timeline, "30-min break")
            stops.append({
                "type": "rest",
                "duration_hours": BREAK_DURATION_HOURS,
                "start_time": stop_time,
                "end_time": state.current_time.isoformat(),
                "mile_marker": round(mile_offset + leg_miles_driven, 1),
            })
