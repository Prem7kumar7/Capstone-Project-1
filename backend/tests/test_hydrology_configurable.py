import pytest
from backend.app.hydrology.config_loader import hydrology_config_manager
from backend.app.hydrology.scs_cn import calculate_scs_cn_runoff
from backend.app.hydrology.rational import calculate_rational_peak_discharge
from backend.app.hydrology.terrain import analyze_terrain_point

def test_hydrology_config_loader():
    config = hydrology_config_manager.get_config()
    assert "curve_numbers" in config
    assert "impervious_paved_roof" in config["curve_numbers"]
    assert config["curve_numbers"]["impervious_paved_roof"]["cn_value"] == 98
    assert config["initial_abstraction_ratio_lambda"] in [0.05, 0.20]

def test_scs_cn_runoff_zero_rain():
    res = calculate_scs_cn_runoff(rainfall_depth_mm=0.0, cn=85)
    assert res["runoff_depth_mm"] == 0.0
    assert res["runoff_volume_m3"] == 0.0

def test_scs_cn_runoff_heavy_rain():
    # 100mm rain on CN 98 should produce high runoff
    res = calculate_scs_cn_runoff(rainfall_depth_mm=100.0, cn=98, area_m2=10000.0)
    assert res["runoff_depth_mm"] > 85.0
    assert res["runoff_volume_m3"] > 850.0

def test_scs_cn_sub_threshold_rain():
    # Rain less than Ia should produce zero runoff
    res = calculate_scs_cn_runoff(rainfall_depth_mm=2.0, cn=60)
    assert res["runoff_depth_mm"] == 0.0

def test_rational_peak_discharge():
    res = calculate_rational_peak_discharge(intensity_mm_h=50.0, area_hectares=2.5, land_cover_type="campus_pavement")
    assert res["peak_discharge_m3_s"] > 0.0
    assert res["c_coefficient"] == 0.85

def test_terrain_analysis():
    # Flat terrain
    flat = analyze_terrain_point(elevation_m=238.0, surrounding_elevations=[238.0, 238.1, 237.9, 238.0])
    assert flat["is_depression"] is False
    assert flat["slope_deg"] < 1.0

    # Low-lying depression (e.g., underpass)
    depression = analyze_terrain_point(elevation_m=233.0, surrounding_elevations=[236.0, 236.5, 235.8, 236.2])
    assert depression["is_depression"] is True
    assert depression["depression_index"] > 2.0
