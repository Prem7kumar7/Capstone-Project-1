import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OPERATIONAL"
    assert "Lovely Professional University" in data["study_area"]

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "HEALTHY"

def test_study_area_endpoints():
    r1 = client.get("/api/v1/study-area")
    assert r1.status_code == 200
    assert r1.json()["study_area_id"] == "lpu_main_campus"

    r2 = client.get("/api/v1/study-area/boundary")
    assert r2.status_code == 200
    assert r2.json()["type"] == "FeatureCollection"

    r3 = client.get("/api/v1/study-area/roads")
    assert r3.status_code == 200
    assert r3.json()["type"] == "FeatureCollection"

    r4 = client.get("/api/v1/study-area/drainage-status")
    assert r4.status_code == 200
    assert r4.json()["drainage_data_availability"] == "NOT_AVAILABLE"

def test_weather_endpoints():
    r = client.get("/api/v1/weather/current")
    assert r.status_code == 200
    data = r.json()
    assert "precipitation_mm_h" in data
    assert data["provenance"] == "LIVE"

    r2 = client.get("/api/v1/weather/forecast")
    assert r2.status_code == 200
    assert r2.json()["forecast_horizon_hours"] == 6

def test_nowcasting_endpoints():
    r = client.get("/api/v1/nowcasting/compare")
    assert r.status_code == 200
    assert len(r.json()["lead_time_comparison"]) > 0

    r2 = client.get("/api/v1/nowcasting/advanced-status")
    assert r2.status_code == 200
    assert r2.json()["optical_flow_module"]["status"] == "AWAITING_RADAR_FEED"

def test_flood_risk_endpoint():
    r = client.get("/api/v1/flood/current-risk")
    assert r.status_code == 200
    data = r.json()
    assert "max_flood_risk_score" in data
    assert "highest_estimated_depth_bracket" in data
    assert len(data["hotspots"]) > 0
    # Verify terminology
    assert "flood_probability" not in str(data).lower()

def test_simulation_run_endpoint():
    payload = {
        "study_area_id": "lpu_main_campus",
        "rainfall_intensity_mm_h": 65.0,
        "cumulative_rainfall_mm": 110.0,
        "storm_duration_hours": 3.0,
        "drainage_clogging_pct": 50.0,
        "scenario_label": "Severe Monsoon Cloudburst Simulation"
    }
    r = client.post("/api/v1/simulation/run", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["is_simulation"] is True
    assert "SIMULATION MODE" in data["simulation_banner"]
    assert data["results"]["max_flood_risk_score"] > 60.0

def test_point_inspection_endpoint():
    payload = {
        "latitude": 31.2530,
        "longitude": 75.6985,
        "study_area_id": "lpu_main_campus"
    }
    r = client.post("/api/v1/flood/inspect-point", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["estimated_depth_label"] == "MODEL ESTIMATE"
    assert data["estimated_time_label"] == "ESTIMATED"
    assert "flood_risk_score" in data

def test_data_health_endpoint():
    r = client.get("/api/v1/data-health/status")
    assert r.status_code == 200
    data = r.json()
    assert len(data["providers"]) >= 5

def test_validation_insufficient_ground_truth_policy():
    r = client.get("/api/v1/validation/metrics")
    assert r.status_code == 200
    data = r.json()
    assert data["validation_status"] == "INSUFFICIENT_GROUND_TRUTH"
    assert data["total_events_recorded"] == 0
    assert "Validation dataset insufficient" in data["message"]

def test_hydrology_config_api():
    r = client.get("/api/v1/hydrology/config")
    assert r.status_code == 200
    data = r.json()
    assert "curve_numbers" in data
    assert data["soil_hydrologic_group"] in ["A", "B", "C", "D"]
