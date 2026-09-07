from typing import Dict, Any
from backend.app.hydrology.config_loader import hydrology_config_manager

def calculate_scs_cn_runoff(rainfall_depth_mm: float, cn: int, area_m2: float = 10000.0) -> Dict[str, float]:
    """
    Computes direct surface runoff depth (mm) and volume (m^3) using the USDA SCS Curve Number Method.
    Data-driven initial abstraction ratio lambda loaded from hydrology configuration.
    
    Formula:
        S = (25400 / CN) - 254  [in mm]
        Ia = lambda * S         [in mm]
        Q = ((P - Ia)^2) / (P - Ia + S)  for P > Ia, else 0
    """
    if cn <= 0 or cn > 100:
        raise ValueError(f"Invalid Curve Number: {cn}. Must be between 1 and 100.")
    if rainfall_depth_mm < 0:
        rainfall_depth_mm = 0.0

    # Potential maximum retention S (mm)
    if cn == 100:
        s_mm = 0.0
        ia_mm = 0.0
        runoff_depth_mm = rainfall_depth_mm
    else:
        s_mm = (25400.0 / float(cn)) - 254.0
        # Configurable initial abstraction ratio
        lambda_ratio = hydrology_config_manager.get_lambda()
        ia_mm = lambda_ratio * s_mm

        if rainfall_depth_mm <= ia_mm:
            runoff_depth_mm = 0.0
        else:
            numerator = (rainfall_depth_mm - ia_mm) ** 2
            denominator = (rainfall_depth_mm - ia_mm) + s_mm
            runoff_depth_mm = numerator / denominator if denominator > 0 else 0.0

    # Runoff volume in cubic meters (m^3)
    # 1 mm depth over 1 m^2 = 0.001 m^3
    runoff_volume_m3 = (runoff_depth_mm / 1000.0) * area_m2

    return {
        "rainfall_depth_mm": round(rainfall_depth_mm, 2),
        "curve_number": cn,
        "potential_retention_s_mm": round(s_mm, 2),
        "initial_abstraction_ia_mm": round(ia_mm, 2),
        "runoff_depth_mm": round(runoff_depth_mm, 2),
        "runoff_volume_m3": round(runoff_volume_m3, 2)
    }
