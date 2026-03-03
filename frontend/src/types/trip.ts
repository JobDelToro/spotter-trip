export interface Location {
  display_name: string;
  lat: number;
  lon: number;
}

export interface TripRequest {
  current_location: string;
  pickup_location: string;
  dropoff_location: string;
  current_cycle_hours: number;
}

export type DutyStatus = "off_duty" | "sleeper_berth" | "driving" | "on_duty";

export interface StatusEntry {
  status: DutyStatus;
  start_hour: number;
  end_hour: number;
  duration_hours: number;
  location: string;
}

export interface ELDLog {
  date: string;
  entries: StatusEntry[];
  total_hours: {
    off_duty: number;
    sleeper_berth: number;
    driving: number;
    on_duty: number;
  };
  remarks: string[];
}

export interface Stop {
  type: "pickup" | "dropoff" | "fuel" | "rest" | "overnight";
  duration_hours: number;
  start_time: string;
  end_time: string;
  mile_marker: number;
  location?: { lat: number; lon: number };
}

export interface TripSummary {
  total_distance_miles: number;
  total_driving_hours: number;
  total_trip_hours: number;
  number_of_stops: number;
  number_of_rest_periods: number;
}

export interface TripResult {
  route: {
    total_distance_miles: number;
    total_duration_hours: number;
    geometry: [number, number][];
    legs: { distance_miles: number; duration_hours: number }[];
  };
  stops: Stop[];
  eld_logs: ELDLog[];
  summary: TripSummary;
}
