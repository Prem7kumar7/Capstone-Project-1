from typing import Dict
from backend.app.hydrology.config_loader import hydrology_config_manager

def calculate_rational_peak_discharge(intensity_mm_h: float, area_hectares: float, land_cover_type: str = "campus_pavement") -> Dict[str, float]:
    """
    Computes peak stormwater discharge using the Rational Method:
        Q_peak = (C * I * A) / 360
    where:
        Q_peak = peak discharge (m^3/s)
        C = dimensionless runoff coefficient
        I = rainfall intensity (mm/hr)
        A = catchment area (hectares)
    """
    config = hydrology_config_manager.get_config()
    c_map = config.get("rational_coefficients", {})
    c = c_map.get(land_cover_type, 0.70)

    if intensity_mm_h <= 0 or area_hectares <= 0:
        return {"peak_discharge_m3_s": 0.0, "c_coefficient": c, "intensity_mm_h": intensity_mm_h, "area_hectares": area_hectares}

    q_peak = (c * intensity_mm_h * area_hectares) / 360.0

    return {
        "peak_discharge_m3_s": round(q_peak, 3),
        "c_coefficient": c,
        "intensity_mm_h": round(intensity_mm_h, 2),
        "area_hectares": round(area_hectares, 2)
    }
