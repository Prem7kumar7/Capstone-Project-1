import pytest
from backend.app.risk.risk_engine import calculate_flood_risk_score
from backend.app.risk.depth_estimator import estimate_water_depth
from backend.app.risk.time_to_flood import calculate_estimated_time_to_flood

def test_risk_score_low_rain():
    res = calculate_flood_risk_score(
        forecast_rainfall_intensity_mm_h=2.0,
        cumulative_rainfall_mm=5.0,
        is_depression=False,
        slope_deg=1.5,
        impervious_fraction=0.3
    )
    assert res["flood_risk_score"] < 40.0
    assert res["risk_category"] in ["VERY_LOW", "LOW"]
    assert res["score_type"] == "ENGINEERING_COMPOSITE_INDEX"

def test_risk_score_extreme_depression_event():
    # Cloudburst over low-lying underpass
    res = calculate_flood_risk_score(
        forecast_rainfall_intensity_mm_h=90.0,
        cumulative_rainfall_mm=140.0,
        is_depression=True,
        depression_drop_m=3.0,
        slope_deg=3.5,
        impervious_fraction=0.95,
        drainage_clogging_fraction=0.5
    )
    assert res["flood_risk_score"] >= 80.0
    assert res["risk_category"] == "EXTREME"

def test_depth_estimator_brackets():
    low_depth = estimate_water_depth(ponding_depth_m=0.03)
    assert low_depth["estimated_depth_bracket"] == "< 0.10 m"
    assert low_depth["provenance_tag"] == "MODEL_ESTIMATE"

    high_depth = estimate_water_depth(ponding_depth_m=0.65, is_depression=True, depression_drop_m=1.0)
    assert high_depth["estimated_depth_bracket"] in ["0.50-1.00 m", "> 1.00 m"]
    assert high_depth["provenance_tag"] == "MODEL_ESTIMATE"

def test_time_to_flood_labels():
    imminent = calculate_estimated_time_to_flood(
        rainfall_intensity_mm_h=60.0,
        current_depth_m=0.18,
        is_depression=True
    )
    assert imminent["provenance_tag"] == "ESTIMATED"
    assert "0-30 min" in imminent["estimated_time_to_flood"]

    dry = calculate_estimated_time_to_flood(
        rainfall_intensity_mm_h=0.0,
        current_depth_m=0.0
    )
    assert dry["urgency"] == "NONE"
