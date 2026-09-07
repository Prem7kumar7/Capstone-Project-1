import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_canonical_regions_endpoint():
    r = client.get("/api/v1/regions")
    assert r.status_code == 200
    data = r.json()
    assert data["total_regions"] == 4
    ids = [reg["id"] for reg in data["study_regions"]]
    assert "lpu_main_campus" in ids
    assert "chaheru" in ids
    assert "phagwara_urban" in ids
    assert "jalandhar_metro" in ids

def test_canonical_rainfall_endpoint():
    r = client.get("/api/v1/rainfall")
    assert r.status_code == 200
    data = r.json()
    assert "value" in data
    assert data["unit"] == "mm/h"
    assert "source_hierarchy" in data
    assert "primary" in data["source_hierarchy"]
    assert "secondary" in data["source_hierarchy"]
    assert "fallback" in data["source_hierarchy"]
    assert data["source_hierarchy"]["primary"]["status"] == "RESTRICTED"

def test_canonical_forecast_endpoint():
    r = client.get("/api/v1/forecast")
    assert r.status_code == 200
    data = r.json()
    assert data["forecast_horizon_hours"] == 6
    assert "cumulative_forecast_6h_mm" in data
    assert len(data["hourly_breakdown"]) > 0

def test_canonical_nowcast_endpoint():
    r = client.get("/api/v1/nowcast?study_area_id=lpu_main_campus")
    assert r.status_code == 200
    data = r.json()
    assert data["system_classification"] == "BASELINE_SHORT_TERM_RAINFALL_NOWCAST"
    assert "AWAITING_RADAR_FEED" in data["radar_feed_status"]
    assert len(data["forecast_horizons"]) == 9

def test_canonical_terrain_endpoint():
    r = client.get("/api/v1/terrain")
    assert r.status_code == 200
    data = r.json()
    assert "regions" in data
    assert "lpu_main_campus" in data["regions"]
    lpu = data["regions"]["lpu_main_campus"]
    assert "elevation" in lpu
    assert "slope" in lpu
    assert "flow_accumulation" in lpu

def test_canonical_flood_risk_endpoint():
    r = client.get("/api/v1/flood-risk?study_area_id=lpu_main_campus")
    assert r.status_code == 200
    data = r.json()
    assert "max_flood_risk_score" in data
    assert data["metric_classification"] == "UNCALIBRATED ENGINEERING RISK INDEX (0-100)"
    assert data["is_statistical_probability"] is False

def test_canonical_flood_susceptibility_endpoint():
    r = client.get("/api/v1/flood-susceptibility?region_id=lpu_main_campus")
    assert r.status_code == 200
    data = r.json()
    assert "land_cover" in data
    assert "susceptibility" in data

def test_canonical_waterways_and_drainage_endpoints():
    r_w = client.get("/api/v1/waterways")
    assert r_w.status_code == 200
    assert r_w.json()["type"] == "FeatureCollection"

    r_d = client.get("/api/v1/drainage")
    assert r_d.status_code == 200
    assert r_d.json()["type"] == "FeatureCollection"

def test_canonical_validation_endpoint():
    r = client.get("/api/v1/validation")
    assert r.status_code == 200
    data = r.json()
    assert data["validation_type"] == "REMOTE_SENSING_VALIDATION_DATA"
    assert data["metrics_summary"]["validation_status"] == "VALIDATED"
    assert data["historical_events_catalog"]["total_events"] == 3

def test_canonical_provenance_endpoint():
    r = client.get("/api/v1/provenance")
    assert r.status_code == 200
    data = r.json()
    assert len(data["datasets"]) >= 8
    statuses = [d["status"] for d in data["datasets"]]
    assert "LIVE" in statuses
    assert "AVAILABLE" in statuses
    assert "UNAVAILABLE" in statuses
    assert "RESTRICTED" in statuses
    assert "HISTORICAL" in statuses
    assert "DERIVED" in statuses
