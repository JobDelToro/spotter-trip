import { MapContainer, TileLayer, Polyline, Marker, Popup } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import type { TripResult } from "../types/trip";
import "./TripMap.css";

// Fix default marker icons in bundled builds
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

const STOP_COLORS: Record<string, string> = {
  pickup: "#16a34a",
  dropoff: "#dc2626",
  fuel: "#f59e0b",
  rest: "#6366f1",
  overnight: "#7c3aed",
};

const STOP_LABELS: Record<string, string> = {
  pickup: "Pickup",
  dropoff: "Drop-off",
  fuel: "Fuel Stop",
  rest: "30-min Break",
  overnight: "Overnight Rest",
};

function makeCircleIcon(color: string) {
  return L.divIcon({
    className: "stop-marker",
    html: `<div style="
      width: 14px; height: 14px;
      background: ${color};
      border: 2px solid #fff;
      border-radius: 50%;
      box-shadow: 0 1px 3px rgba(0,0,0,0.3);
    "></div>`,
    iconSize: [14, 14],
    iconAnchor: [7, 7],
  });
}

function formatTime(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

interface Props {
  trip: TripResult;
}

export default function TripMap({ trip }: Props) {
  const { route, stops } = trip;
  const positions = route.geometry as [number, number][];

  // Compute bounds for auto-fit
  const bounds = L.latLngBounds(positions.map(([lat, lon]) => [lat, lon]));

  return (
    <div className="trip-map">
      <MapContainer
        bounds={bounds}
        boundsOptions={{ padding: [40, 40] }}
        scrollWheelZoom={true}
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <Polyline positions={positions} color="#3b82f6" weight={4} opacity={0.8} />

        {/* Start marker */}
        {positions.length > 0 && (
          <Marker position={positions[0]}>
            <Popup>Start location</Popup>
          </Marker>
        )}

        {/* End marker */}
        {positions.length > 1 && (
          <Marker position={positions[positions.length - 1]}>
            <Popup>Final destination</Popup>
          </Marker>
        )}

        {/* Stop markers */}
        {stops.map((stop, i) => {
          if (!stop.location) return null;
          const color = STOP_COLORS[stop.type] || "#6b7280";
          const label = STOP_LABELS[stop.type] || stop.type;
          return (
            <Marker
              key={i}
              position={[stop.location.lat, stop.location.lon]}
              icon={makeCircleIcon(color)}
            >
              <Popup>
                <strong>{label}</strong>
                <br />
                {formatTime(stop.start_time)}
                <br />
                {stop.duration_hours}h stop
                <br />
                Mile {Math.round(stop.mile_marker)}
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
}
