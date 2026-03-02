from datetime import datetime, timedelta
from collections import defaultdict


STATUS_MAP = {
    "off_duty": "off_duty",
    "sleeper_berth": "sleeper_berth",
    "driving": "driving",
    "on_duty": "on_duty",
}


def generate_eld_logs(timeline: list[dict]) -> list[dict]:
    """
    Convert a trip timeline into daily ELD log sheets.

    Each log covers one 24-hour period (midnight to midnight)
    and contains the duty status entries for that day.
    """
    if not timeline:
        return []

    first_start = datetime.fromisoformat(timeline[0]["start_time"])
    last_end = datetime.fromisoformat(timeline[-1]["end_time"])

    # Figure out all dates covered
    start_date = first_start.date()
    end_date = last_end.date()

    logs_by_date = {}
    current_date = start_date
    while current_date <= end_date:
        logs_by_date[current_date] = {
            "date": current_date.isoformat(),
            "entries": [],
            "total_hours": {
                "off_duty": 0,
                "sleeper_berth": 0,
                "driving": 0,
                "on_duty": 0,
            },
            "remarks": [],
        }
        current_date += timedelta(days=1)

    # Split each timeline entry across day boundaries
    for entry in timeline:
        entry_start = datetime.fromisoformat(entry["start_time"])
        entry_end = datetime.fromisoformat(entry["end_time"])
        status = STATUS_MAP.get(entry["status"], entry["status"])
        location = entry.get("location", "")

        current = entry_start
        while current < entry_end:
            day = current.date()
            day_midnight = datetime.combine(
                day + timedelta(days=1), datetime.min.time()
            )
            segment_end = min(entry_end, day_midnight)
            duration = (segment_end - current).total_seconds() / 3600

            if duration > 0 and day in logs_by_date:
                log = logs_by_date[day]
                log["entries"].append({
                    "status": status,
                    "start_hour": current.hour + current.minute / 60,
                    "end_hour": (
                        segment_end.hour + segment_end.minute / 60
                        if segment_end.date() == day
                        else 24.0
                    ),
                    "duration_hours": round(duration, 2),
                    "location": location,
                })
                log["total_hours"][status] = round(
                    log["total_hours"][status] + duration, 2
                )

                if location and location not in log["remarks"]:
                    log["remarks"].append(location)

            current = segment_end

    # Fill gaps at start/end of each day with off-duty
    for date, log in logs_by_date.items():
        entries = log["entries"]
        if not entries:
            log["entries"].append({
                "status": "off_duty",
                "start_hour": 0,
                "end_hour": 24,
                "duration_hours": 24,
                "location": "",
            })
            log["total_hours"]["off_duty"] = 24
            continue

        # Fill from midnight to first entry
        first = entries[0]
        if first["start_hour"] > 0:
            gap_hours = first["start_hour"]
            entries.insert(0, {
                "status": "off_duty",
                "start_hour": 0,
                "end_hour": first["start_hour"],
                "duration_hours": round(gap_hours, 2),
                "location": "",
            })
            log["total_hours"]["off_duty"] = round(
                log["total_hours"]["off_duty"] + gap_hours, 2
            )

        # Fill from last entry to midnight
        last = entries[-1]
        if last["end_hour"] < 24:
            gap_hours = 24 - last["end_hour"]
            entries.append({
                "status": "off_duty",
                "start_hour": last["end_hour"],
                "end_hour": 24,
                "duration_hours": round(gap_hours, 2),
                "location": "",
            })
            log["total_hours"]["off_duty"] = round(
                log["total_hours"]["off_duty"] + gap_hours, 2
            )

    # Return sorted by date
    return [logs_by_date[d] for d in sorted(logs_by_date.keys())]
