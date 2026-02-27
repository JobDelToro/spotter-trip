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
  start_time: string;
  end_time: string;
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
  type: "start" | "pickup" | "dropoff" | "fuel" | "rest" | "overnight";
  location: string;
  lat: number;
  lon: number;
  arrival_time: string;
  departure_time: string;
  duration_hours: number;
}

export interface TripResult {
  route: {
    total_distance_miles: number;
    total_duration_hours: number;
    geometry: [number, number][];
  };
  stops: Stop[];
  eld_logs: ELDLog[];
}
