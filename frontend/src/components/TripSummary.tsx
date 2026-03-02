import type { TripResult } from "../types/trip";
import "./TripSummary.css";

const STOP_LABELS: Record<string, string> = {
  pickup: "Pickup",
  dropoff: "Drop-off",
  fuel: "Fuel Stop",
  rest: "30-min Break",
  overnight: "Overnight Rest",
};

function formatTime(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

interface Props {
  trip: TripResult;
}

export default function TripSummary({ trip }: Props) {
  const { summary, stops } = trip;

  return (
    <div className="trip-summary">
      <div className="summary-stats">
        <div className="stat">
          <span className="stat-value">
            {summary.total_distance_miles.toLocaleString()}
          </span>
          <span className="stat-label">miles</span>
        </div>
        <div className="stat">
          <span className="stat-value">{summary.total_driving_hours}</span>
          <span className="stat-label">driving hrs</span>
        </div>
        <div className="stat">
          <span className="stat-value">{summary.total_trip_hours}</span>
          <span className="stat-label">total hrs</span>
        </div>
        <div className="stat">
          <span className="stat-value">{summary.number_of_stops}</span>
          <span className="stat-label">stops</span>
        </div>
      </div>

      <div className="stops-list">
        <h3>Stops</h3>
        {stops.map((stop, i) => (
          <div key={i} className={`stop-item stop-${stop.type}`}>
            <div className="stop-dot" />
            <div className="stop-info">
              <span className="stop-type">
                {STOP_LABELS[stop.type] || stop.type}
              </span>
              <span className="stop-time">{formatTime(stop.start_time)}</span>
              <span className="stop-detail">
                Mile {Math.round(stop.mile_marker)} &middot;{" "}
                {stop.duration_hours}h
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
