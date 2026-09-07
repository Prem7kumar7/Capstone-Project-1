from typing import Dict, Any
from backend.app.hydrology.scs_cn import calculate_scs_cn_runoff
from backend.app.hydrology.rational import calculate_rational_peak_discharge

def evaluate_simplified_drainage_limitation(
    rainfall_intensity_mm_h: float,
    cumulative_rainfall_mm: float,
    cn: int,
    area_m2: float = 10000.0,
    is_depression: bool = False,
    depression_drop_m: float = 0.0,
    drainage_clogging_fraction: float = 0.0,
    drainage_available: bool = False
) -> Dict[str, Any]:
    """
    Simplified Runoff & Drainage Limitation Model (Active Mode).
    
    Operates without pretending to know underground pipe invert levels.
    Combines SCS-CN surface runoff volume, peak discharge, overland slope conveyance,
    and drainage clogging fraction to estimate overland accumulation and surcharging.
    """
    area_ha = area_m2 / 10000.0
    
    # 1. SCS-CN Runoff depth and volume
    scs_res = calculate_scs_cn_runoff(cumulative_rainfall_mm, cn, area_m2)
    runoff_depth_mm = scs_res["runoff_depth_mm"]
    runoff_vol_m3 = scs_res["runoff_volume_m3"]

    # 2. Rational peak discharge
    peak_res = calculate_rational_peak_discharge(rainfall_intensity_mm_h, area_ha)
    peak_q = peak_res["peak_discharge_m3_s"]

    # 3. Drainage conveyance capacity estimate
    # When drainage is NOT surveyed/available, base conveyance capacity is minimal
    if not drainage_available:
        nominal_capacity_m3_s = 0.5 * area_ha  # Natural overland percolation/ditch seepage
    else:
        nominal_capacity_m3_s = 2.5 * area_ha  # Standard storm drain conveyance

    # Apply clogging fraction
    effective_capacity_m3_s = nominal_capacity_m3_s * max(0.0, (1.0 - drainage_clogging_fraction))

    # Inadequacy ratio
    surcharge_ratio = peak_q / max(effective_capacity_m3_s, 0.01)

    # 4. Overland accumulation depth proxy (m)
    # If in a low-lying depression or surcharging
    if is_depression:
        # Trapped water accumulates in depression
        trapped_vol_m3 = runoff_vol_m3 * 0.6  # 60% drains toward depression
        effective_ponding_area = area_m2 * 0.4
        ponding_depth_m = trapped_vol_m3 / max(effective_ponding_area, 100.0)
    else:
        # Overland sheet flow with runoff depth converted to ponding/sheet depth
        ponding_depth_m = (runoff_depth_mm / 1000.0) * min(surcharge_ratio, 3.0)

    return {
        "modelling_mode": "SIMPLIFIED_RUNOFF_LIMITATION",
        "drainage_data_availability": "LIMITED" if drainage_available else "NOT_AVAILABLE",
        "runoff_depth_mm": runoff_depth_mm,
        "runoff_volume_m3": runoff_vol_m3,
        "peak_discharge_m3_s": peak_q,
        "effective_drainage_capacity_m3_s": round(effective_capacity_m3_s, 3),
        "surcharge_ratio": round(surcharge_ratio, 2),
        "estimated_ponding_depth_m": round(ponding_depth_m, 3),
        "clogging_fraction_applied": drainage_clogging_fraction
    }
