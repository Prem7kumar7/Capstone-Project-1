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
    data = r1.json()
    assert data["study_area_id"] == "lpu_main_campus"
    assert len(data["available_areas"]) == 4

    # Test all 4 regions boundaries
    for reg_id in ["lpu_main_campus", "chaheru", "phagwara_urban", "jalandhar_metro"]:
        r_b = client.get(f"/api/v1/study-area/boundary?region_id={reg_id}")
        assert r_b.status_code == 200
        assert r_b.json()["type"] == "FeatureCollection"

    # Test natural waterways vs urban drainage separation
    r_w = client.get("/api/v1/study-area/waterways")
    assert r_w.status_code == 200
    assert r_w.json()["type"] == "FeatureCollection"

    r_nw = client.get("/api/v1/study-area/natural-waterways")
    assert r_nw.status_code == 200
    assert r_nw.json()["type"] == "FeatureCollection"
    assert any("Kali Bein" in f.get("properties", {}).get("name", "") for f in r_nw.json()["features"])

    r_ud = client.get("/api/v1/study-area/urban-drainage")
    assert r_ud.status_code == 200
    assert r_ud.json()["type"] == "FeatureCollection"
    assert any("Kala Sanghian" in f.get("properties", {}).get("name", "") for f in r_ud.json()["features"])

    r_inf = client.get("/api/v1/study-area/infrastructure")
    assert r_inf.status_code == 200
    assert r_inf.json()["type"] == "FeatureCollection"

    # Test drainage status (transparent declaration)
    r4 = client.get("/api/v1/study-area/drainage-status")
    assert r4.status_code == 200
    assert "LEVEL_2" in r4.json()["drainage_data_availability"]

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

    r3 = client.get("/api/v1/nowcasting/timeline?study_area_id=lpu_main_campus")
    assert r3.status_code == 200
    timeline = r3.json()["forecast_horizons"]
    assert len(timeline) == 9 # 0h, 15m, 30m, 1h, 2h, 3h, 4h, 5h, 6h
    assert timeline[0]["label"] == "Now (0h)"

def test_flood_risk_endpoint():
    r = client.get("/api/v1/flood/current-risk")
    assert r.status_code == 200
    data = r.json()
    assert "max_flood_risk_score" in data
    assert "highest_estimated_depth_bracket" in data
    assert len(data["hotspots"]) > 0
    # Verify candidate node labeling (no fake verified sensor claim)
    h0 = data["hotspots"][0]
    assert h0["node_classification"] == "MODEL_DERIVED_CANDIDATE"
    assert h0["is_field_verified_sensor"] is False
    assert "MODEL-DERIVED CANDIDATE" in h0["node_status_label"]
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

def test_validation_satellite_ground_truth():
    # Test catalog of independent historical events
    r_ev = client.get("/api/v1/validation/historical-events")
    assert r_ev.status_code == 200
    ev_data = r_ev.json()
    assert ev_data["total_events"] == 3
    event_ids = [e["event_id"] for e in ev_data["events"]]
    assert "EV-2019-08-PUNJAB-SUTLEJ-DELUGE" in event_ids
    assert "EV-2020-08-JALANDHAR-CLOUDBURST" in event_ids
    assert "EV-2023-07-PUNJAB-MONSOON-DELUGE" in event_ids

    # Test aggregate validation metrics across historical events
    r = client.get("/api/v1/validation/metrics")
    assert r.status_code == 200
    data = r.json()
    assert data["validation_status"] == "VALIDATED"
    assert data["total_events_recorded"] == 22
    assert data["metrics"] is not None
    # Scientific realistic metrics (incorporating unmapped pumping FPs and debris clogging FNs)
    assert 0.75 <= data["metrics"]["precision"] <= 0.95
    assert 0.75 <= data["metrics"]["recall"] <= 0.95
    assert data["metrics"]["f1_score"] > 0.80
    assert data["metrics"]["depth_mae_m"] is not None
    assert data["metrics"]["depth_mae_m"] < 0.20

def test_hydrology_config_api():
    r = client.get("/api/v1/hydrology/config")
    assert r.status_code == 200
    data = r.json()
    assert "curve_numbers" in data
    assert data["soil_hydrologic_group"] in ["A", "B", "C", "D"]
