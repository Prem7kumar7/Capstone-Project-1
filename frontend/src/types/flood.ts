export interface WeatherCurrent {
  study_area_id: string;
  timestamp_utc: string;
  timestamp_ist: string;
  temperature_c: number | null;
  relative_humidity_pct: number | null;
  precipitation_mm_h: number;
  rain_mm: number | null;
  wind_speed_kmh: number | null;
  weather_code: number | null;
  weather_condition: string;
  data_source: string;
  provenance: "LIVE" | "HISTORICAL" | "SIMULATED";
  status: string;
}

export interface HourlyForecastItem {
  timestamp_utc: string;
  timestamp_ist: string;
  precipitation_mm: number;
  precipitation_probability_pct: number | null;
  temperature_c: number | null;
  weather_code: number | null;
}

export interface WeatherForecast {
  study_area_id: string;
  issued_at_utc: string;
  issued_at_ist: string;
  forecast_horizon_hours: number;
  cumulative_forecast_6h_mm: number;
  max_forecast_intensity_mm_h: number;
  hourly: HourlyForecastItem[];
  data_source: string;
  provenance: string;
  model_name: string;
  status: string;
}

export interface FloodHotspot {
  id: number;
  location_name: string;
  latitude: number;
  longitude: number;
  elevation_m: number | null;
  flood_risk_score: number; // 0 to 100
  risk_category: "VERY_LOW" | "LOW" | "MODERATE" | "HIGH" | "EXTREME";
  estimated_depth_bracket: string;
  estimated_depth_label: string; // "MODEL ESTIMATE"
  estimated_time_to_flood: string;
  estimated_time_label: string; // "ESTIMATED"
  susceptibility_factors?: {
    is_depression: boolean;
    slope_deg: number;
    land_cover: string;
    curve_number: number;
    surcharge_ratio: number;
    notes?: string;
  };
  data_provenance: string;
}

export interface FloodPredictionRun {
  run_id: string;
  study_area_id: string;
  run_timestamp_utc: string;
  run_timestamp_ist: string;
  execution_mode: "LIVE" | "SIMULATED";
  modelling_mode: string;
  current_rainfall_mm_h: number;
  forecast_cumulative_6h_mm: number;
  max_forecast_intensity_mm_h: number;
  drainage_clogging_fraction: number;
  max_flood_risk_score: number;
  overall_severity: "VERY_LOW" | "LOW" | "MODERATE" | "HIGH" | "EXTREME";
  highest_estimated_depth_bracket: string;
  earliest_time_to_flood: string;
  affected_hotspots_count: number;
  confidence_level: "HIGH" | "MEDIUM" | "LOW";
  data_sources: string[];
  model_version: string;
  is_simulation: boolean;
  hotspots: FloodHotspot[];
}

export interface AlertAdvisory {
  id: string;
  study_area_id: string;
  alert_level: "GREEN" | "YELLOW" | "ORANGE" | "RED";
  headline: string;
  location_name: string;
  forecast_rainfall_summary: string;
  flood_risk_score: number;
  estimated_depth_bracket: string;
  estimated_time_to_impact: string;
  recommended_actions: string;
  data_source: string;
  provenance: string;
  issued_at_ist: string;
  is_simulation: boolean;
}

export interface ProviderStatus {
  provider_name: string;
  provider_type: string;
  status: "ONLINE" | "DEGRADED" | "OFFLINE" | "DORMANT" | "NOT_AVAILABLE";
  latency_ms: number | null;
  last_updated_ist: string;
  data_provenance: string;
  notes?: string;
}

export interface SystemHealth {
  system_status: "OPERATIONAL" | "DEGRADED" | "OFFLINE";
  active_study_area: string;
  checked_at_ist: string;
  providers: ProviderStatus[];
}

export interface PointInspectionResult {
  latitude: number;
  longitude: number;
  location_label: string;
  elevation_m: number;
  slope_deg: number;
  is_depression: boolean;
  land_cover_type: string;
  curve_number: number;
  current_rainfall_mm_h: number;
  forecast_cumulative_6h_mm: number;
  runoff_depth_mm: number;
  flood_risk_score: number;
  risk_category: string;
  estimated_depth_bracket: string;
  estimated_depth_label: string;
  estimated_time_to_flood: string;
  estimated_time_label: string;
  data_source: string;
  provenance: string;
  confidence: string;
  updated_at_ist: string;
}
