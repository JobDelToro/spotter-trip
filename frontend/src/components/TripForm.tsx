import { useState } from "react";
import LocationInput from "./LocationInput";
import type { Location, TripRequest } from "../types/trip";
import "./TripForm.css";

interface TripFormProps {
  onSubmit: (data: TripRequest) => void;
  loading?: boolean;
}

export default function TripForm({ onSubmit, loading }: TripFormProps) {
  const [currentLoc, setCurrentLoc] = useState<Location | null>(null);
  const [pickupLoc, setPickupLoc] = useState<Location | null>(null);
  const [dropoffLoc, setDropoffLoc] = useState<Location | null>(null);
  const [cycleHours, setCycleHours] = useState<string>("0");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    if (!currentLoc || !pickupLoc || !dropoffLoc) return;

    const hours = parseFloat(cycleHours);
    if (isNaN(hours) || hours < 0 || hours > 70) return;

    onSubmit({
      current_location: `${currentLoc.lat},${currentLoc.lon}`,
      pickup_location: `${pickupLoc.lat},${pickupLoc.lon}`,
      dropoff_location: `${dropoffLoc.lat},${dropoffLoc.lon}`,
      current_cycle_hours: hours,
    });
  }

  const isValid = currentLoc && pickupLoc && dropoffLoc;

  return (
    <form className="trip-form" onSubmit={handleSubmit}>
      <LocationInput
        label="Current Location"
        placeholder="Where are you now?"
        onSelect={setCurrentLoc}
      />
      <LocationInput
        label="Pickup Location"
        placeholder="Where to pick up?"
        onSelect={setPickupLoc}
      />
      <LocationInput
        label="Drop-off Location"
        placeholder="Where to deliver?"
        onSelect={setDropoffLoc}
      />
      <div className="trip-form__field">
        <label className="location-input__label">
          Current Cycle Hours Used
        </label>
        <input
          type="number"
          className="location-input__field"
          placeholder="0"
          min="0"
          max="70"
          step="0.5"
          value={cycleHours}
          onChange={(e) => setCycleHours(e.target.value)}
        />
        <span className="trip-form__hint">
          Hours used in current 70-hour/8-day cycle (0–70)
        </span>
      </div>
      <button
        type="submit"
        className="trip-form__submit"
        disabled={!isValid || loading}
      >
        {loading ? "Planning trip..." : "Plan Trip"}
      </button>
    </form>
  );
}
