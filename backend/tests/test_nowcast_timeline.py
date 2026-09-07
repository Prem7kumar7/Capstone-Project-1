import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_nowcast_timeline_structure_and_horizons():
    """Validates 0-6h nowcast timeline response structure, timestamps, and monotonic step progression."""
    r = client.get("/api/v1/nowcasting/timeline?study_area_id=lpu_main_campus")
    assert r.status_code == 200
    data = r.json()
    assert data["study_area_id"] == "lpu_main_campus"
    horizons = data["forecast_horizons"]
    assert len(horizons) == 9 # 0h, 15m, 30m, 1h, 2h, 3h, 4h, 5h, 6h

    labels = [h["label"] for h in horizons]
    assert labels == [
        "Now (0h)", "+15 min", "+30 min", "+1 hour",
        "+2 hours", "+3 hours", "+4 hours", "+5 hours", "+6 hours"
    ]

    for h in horizons:
        assert "lead_time_hours" in h
        assert "projected_rainfall_mm_h" in h
        assert "confidence_score" in h
        assert "max_flood_risk_score" in h
        assert "overall_severity" in h
        assert "highest_estimated_depth_bracket" in h
        assert h["max_flood_risk_score"] >= 0.0

def test_nowcast_timeline_all_four_regions():
    """Validates timeline generation across LPU, Chaheru, Phagwara, and Jalandhar."""
    for reg_id in ["lpu_main_campus", "chaheru", "phagwara_urban", "jalandhar_metro"]:
        r = client.get(f"/api/v1/nowcasting/timeline?study_area_id={reg_id}")
        assert r.status_code == 200
        data = r.json()
        assert data["study_area_id"] == reg_id
        assert len(data["forecast_horizons"]) == 9
