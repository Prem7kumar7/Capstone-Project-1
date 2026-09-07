import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

REGIONS = ["lpu_main_campus", "chaheru", "phagwara_urban", "jalandhar_metro"]

def test_all_four_study_regions_accessible():
    for reg_id in REGIONS:
        r = client.get(f"/api/v1/study-area?region_id={reg_id}")
        assert r.status_code == 200
        data = r.json()
        assert data["study_area_id"] == reg_id
        assert data["elevation_base_m"] > 220.0
        assert "centroid" in data

def test_all_four_study_regions_boundaries():
    for reg_id in REGIONS:
        r = client.get(f"/api/v1/study-area/boundary?region_id={reg_id}")
        assert r.status_code == 200
        geojson = r.json()
        assert geojson["type"] == "FeatureCollection"
        assert len(geojson["features"]) > 0

def test_multi_region_flood_risk():
    for reg_id in REGIONS:
        r = client.get(f"/api/v1/flood/current-risk?study_area_id={reg_id}")
        assert r.status_code == 200
        data = r.json()
        assert data["study_area_id"] == reg_id
        assert "hotspots" in data
        assert len(data["hotspots"]) >= 4

def test_nowcast_timeline_horizons():
    r = client.get("/api/v1/nowcasting/timeline?study_area_id=chaheru")
    assert r.status_code == 200
    data = r.json()
    assert data["study_area_id"] == "chaheru"
    horizons = data["forecast_horizons"]
    assert len(horizons) == 9
    assert horizons[1]["label"] == "+15 min"
    assert horizons[2]["label"] == "+30 min"
    assert horizons[8]["label"] == "+6 hours"
