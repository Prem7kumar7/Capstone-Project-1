from typing import Dict, Any
from backend.app.hydrology.config_loader import hydrology_config_manager

def calculate_flood_risk_score(
    forecast_rainfall_intensity_mm_h: float,
    cumulative_rainfall_mm: float,
    is_depression: bool = False,
    depression_drop_m: float = 0.0,
    slope_deg: float = 1.0,
    impervious_fraction: float = 0.5,
    drainage_clogging_fraction: float = 0.0,
    drainage_available: bool = False
) -> Dict[str, Any]:
    """
    Computes the composite Flood Risk Score (scale 0 - 100).
    
    IMPORTANT SCIENTIFIC TRANSPARENCY:
    This is an engineering risk index, NOT a frequentist/Bayesian statistical probability.
    Weights are data-driven and loaded from hydrology_params.json.
    """
    config = hydrology_config_manager.get_config()
    weights = config.get("risk_score_weights", {
        "forecast_rainfall_intensity": 0.30,
        "cumulative_rainfall": 0.20,
        "terrain_depression_index": 0.25,
        "drainage_inadequacy_proxy": 0.15,
        "impervious_fraction": 0.10
    })

    # Factor 1: Rainfall Intensity factor (0 - 100)
    # 0 mm/h -> 0, >= 80 mm/h -> 100
    f_intensity = min(100.0, (forecast_rainfall_intensity_mm_h / 80.0) * 100.0)

    # Factor 2: Cumulative Rainfall factor (0 - 100)
    # 0 mm -> 0, >= 150 mm -> 100
    f_cumulative = min(100.0, (cumulative_rainfall_mm / 150.0) * 100.0)

    # Factor 3: Topographic Depression & Slope factor (0 - 100)
    # Flat / depressed areas have higher water accumulation potential
    f_depression = 20.0  # Baseline flat terrain
    if is_depression:
        # Extra score proportional to depression depth
        f_depression = min(100.0, 50.0 + (depression_drop_m * 30.0))
    else:
        # Mild relief drains better
        if slope_deg > 2.0:
            f_depression = max(5.0, 30.0 - (slope_deg * 5.0))

    # Factor 4: Drainage Inadequacy / Clogging factor (0 - 100)
    if not drainage_available:
        f_drainage = 70.0 + (drainage_clogging_fraction * 30.0)
    else:
        f_drainage = 20.0 + (drainage_clogging_fraction * 80.0)

    # Factor 5: Impervious Surface Fraction (0 - 100)
    f_impervious = min(100.0, impervious_fraction * 100.0)

    # Compute weighted composite score
    w_int = weights.get("forecast_rainfall_intensity", 0.30)
    w_cum = weights.get("cumulative_rainfall", 0.20)
    w_dep = weights.get("terrain_depression_index", 0.25)
    w_drn = weights.get("drainage_inadequacy_proxy", 0.15)
    w_imp = weights.get("impervious_fraction", 0.10)

    total_weight = w_int + w_cum + w_dep + w_drn + w_imp
    raw_score = (
        (f_intensity * w_int) +
        (f_cumulative * w_cum) +
        (f_depression * w_dep) +
        (f_drainage * w_drn) +
        (f_impervious * w_imp)
    ) / total_weight

    score = round(max(0.0, min(100.0, raw_score)), 1)

    # Categorize risk level
    if score < 20.0:
        category = "VERY_LOW"
    elif score < 40.0:
        category = "LOW"
    elif score < 60.0:
        category = "MODERATE"
    elif score < 80.0:
        category = "HIGH"
    else:
        category = "EXTREME"

    return {
        "flood_risk_score": score,
        "risk_category": category,
        "score_type": "ENGINEERING_COMPOSITE_INDEX",
        "factor_breakdown": {
            "rainfall_intensity_score": round(f_intensity, 1),
            "cumulative_rainfall_score": round(f_cumulative, 1),
            "terrain_depression_score": round(f_depression, 1),
            "drainage_inadequacy_score": round(f_drainage, 1),
            "impervious_surface_score": round(f_impervious, 1)
        }
    }
