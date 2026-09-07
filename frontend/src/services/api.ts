import {
  WeatherCurrent,
  WeatherForecast,
  FloodPredictionRun,
  AlertAdvisory,
  SystemHealth,
  PointInspectionResult
} from "@/types/flood";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

export async function fetchCurrentWeather(): Promise<WeatherCurrent> {
  const res = await fetch(`${API_BASE}/weather/current`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Weather fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchWeatherForecast(): Promise<WeatherForecast> {
  const res = await fetch(`${API_BASE}/weather/forecast`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Forecast fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchCurrentFloodRisk(): Promise<FloodPredictionRun> {
  const res = await fetch(`${API_BASE}/flood/current-risk`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Flood risk fetch failed: ${res.statusText}`);
  return res.json();
}

export async function runSimulationScenario(scenario: {
  study_area_id: string;
  rainfall_intensity_mm_h: number;
  cumulative_rainfall_mm: number;
  storm_duration_hours: number;
  drainage_clogging_pct: number;
  scenario_label: string;
}): Promise<{ simulation_banner: string; is_simulation: boolean; results: FloodPredictionRun }> {
  const res = await fetch(`${API_BASE}/simulation/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(scenario),
  });
  if (!res.ok) throw new Error(`Simulation failed: ${res.statusText}`);
  return res.json();
}

export async function inspectLocationPoint(
  lat: number,
  lon: number
): Promise<PointInspectionResult> {
  const res = await fetch(`${API_BASE}/flood/inspect-point`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ latitude: lat, longitude: lon }),
  });
  if (!res.ok) throw new Error(`Point inspection failed: ${res.statusText}`);
  return res.json();
}

export async function fetchActiveAlerts(isSimulation = false): Promise<AlertAdvisory[]> {
  const res = await fetch(`${API_BASE}/alerts/active?is_simulation=${isSimulation}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Alerts fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchSystemHealth(): Promise<SystemHealth> {
  const res = await fetch(`${API_BASE}/data-health/status`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Health status fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchBoundaryGeoJson(): Promise<any> {
  const res = await fetch(`${API_BASE}/study-area/boundary`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Boundary fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchRoadsGeoJson(): Promise<any> {
  const res = await fetch(`${API_BASE}/study-area/roads`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Roads fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchValidationMetrics(): Promise<any> {
  const res = await fetch(`${API_BASE}/validation/metrics`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Validation metrics fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchHydrologyConfig(): Promise<any> {
  const res = await fetch(`${API_BASE}/hydrology/config`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Hydrology config fetch failed: ${res.statusText}`);
  return res.json();
}

export async function updateHydrologyConfig(data: any): Promise<any> {
  const res = await fetch(`${API_BASE}/hydrology/config`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`Config update failed: ${res.statusText}`);
  return res.json();
}
