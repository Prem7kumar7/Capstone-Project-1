# REST API Documentation

The Urban Flood Nowcasting platform provides fully documented RESTful APIs with OpenAPI/Swagger specifications at `/docs`.

Base URL: `http://localhost:8000/api/v1`

---

## Endpoint Catalog

### 1. Study Area & Geospatial Layers
- **`GET /api/v1/study-area`**: Returns primary study area metadata, centroid coordinates, and expandable city boundaries.
- **`GET /api/v1/study-area/boundary`**: Returns verified OpenStreetMap GeoJSON polygon for LPU campus (OSM Way `422435593`).
- **`GET /api/v1/study-area/roads`**: Returns verified OpenStreetMap GeoJSON line strings for the NH-44 Grand Trunk Road corridor.
- **`GET /api/v1/study-area/drainage-status`**: Transparently returns sub-surface drainage data availability status (`NOT_AVAILABLE`).

### 2. Weather & Forecast Ingestion
- **`GET /api/v1/weather/current`**: Returns real-time weather observations from Open-Meteo with provenance tag (`LIVE`).
- **`GET /api/v1/weather/forecast`**: Returns 0–6 hour numerical weather prediction forecast with hourly rain rates and cumulative totals (`FORECAST`).

### 3. Nowcasting Comparison & Advanced Modules
- **`GET /api/v1/nowcasting/compare`**: Compares NWP forecasts, Eulerian persistence decay models, and trend extrapolation.
- **`GET /api/v1/nowcasting/advanced-status`**: Returns operational state and data prerequisites for the 2D optical flow advection engine and ConvLSTM deep learning interface.

### 4. Flood Risk & Point Inspection
- **`GET /api/v1/flood/current-risk`**: Executes the live nowcasting pipeline across verified campus monitoring nodes.
- **`POST /api/v1/flood/inspect-point`**: On-demand point inspection taking `{"latitude": float, "longitude": float}` and returning elevation, slope, SCS-CN runoff, Flood Risk Score, estimated depth bracket, and estimated time-to-flood.

### 5. What-If Scenario Simulation
- **`POST /api/v1/simulation/run`**:
  ```json
  {
    "study_area_id": "lpu_main_campus",
    "rainfall_intensity_mm_h": 65.0,
    "cumulative_rainfall_mm": 110.0,
    "storm_duration_hours": 3.0,
    "drainage_clogging_pct": 40.0,
    "scenario_label": "Severe Cloudburst with 40% Clogged Drains"
  }
  ```
  Returns full hydrological model results tagged strictly as `SIMULATED` with an unmissable disclaimer banner.

### 6. Emergency Alerts & Advisories
- **`GET /api/v1/alerts/active`**: Returns color-coded advisories (GREEN, YELLOW, ORANGE, RED) with actionable instructions and timestamps in IST.
- **`GET /api/v1/alerts/thresholds`**: Returns configurable engineering alert thresholds.
- **`PUT /api/v1/alerts/thresholds/{level}`**: Updates alert trigger levels.

### 7. Data Health & Provenance
- **`GET /api/v1/data-health/status`**: Returns real-time provider connectivity, latency, last response time, and data provenance tags.

### 8. Scientific Validation
- **`GET /api/v1/validation/metrics`**: Returns empirical backtesting metrics (MAE, RMSE, Precision, Recall, F1). Reports `INSUFFICIENT_GROUND_TRUTH` if 0 field events are logged.
- **`POST /api/v1/validation/record-observation`**: Registers genuine field observations during storm events.

### 9. Hydrology Configuration
- **`GET /api/v1/hydrology/config`**: Returns data-driven SCS-CN tables, soil groups, and roughness parameters.
- **`PUT /api/v1/hydrology/config`**: Calibrates parameters at runtime.
