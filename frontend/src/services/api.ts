const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export async function searchLocations(query: string): Promise<
  { display_name: string; lat: number; lon: number }[]
> {
  const res = await fetch(
    `${API_BASE}/locations/search?q=${encodeURIComponent(query)}`
  );
  if (!res.ok) return [];
  return res.json();
}

export async function planTrip(data: {
  current_location: string;
  pickup_location: string;
  dropoff_location: string;
  current_cycle_hours: number;
}) {
  const res = await fetch(`${API_BASE}/trip/plan`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to plan trip");
  }
  return res.json();
}
