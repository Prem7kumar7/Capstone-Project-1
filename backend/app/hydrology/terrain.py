import math
from typing import Dict, Any, List

def analyze_terrain_point(elevation_m: float, surrounding_elevations: List[float], cell_size_m: float = 30.0) -> Dict[str, Any]:
    """
    Computes topographic characteristics for a point:
    - Slope (degrees and percentage)
    - Depression index (relative drop compared to surroundings)
    - Topographic Wetness Index (TWI) proxy
    """
    if not surrounding_elevations:
        return {
            "elevation_m": elevation_m,
            "slope_deg": 0.5,
            "slope_pct": 0.87,
            "depression_index": 0.0,
            "is_depression": False,
            "twi_proxy": 5.0
        }

    mean_surrounding = sum(surrounding_elevations) / len(surrounding_elevations)
    max_surrounding = max(surrounding_elevations)
    min_surrounding = min(surrounding_elevations)

    # Elevation drop/rise
    delta_z = max_surrounding - min_surrounding
    # Approximation of gradient across neighborhood
    distance = cell_size_m * math.sqrt(2)
    slope_rad = math.atan(max(delta_z, 0.01) / distance)
    slope_deg = math.degrees(slope_rad)
    slope_pct = math.tan(slope_rad) * 100.0

    # Depression index: positive if point is lower than surrounding average
    depression_drop = mean_surrounding - elevation_m
    is_depression = depression_drop > 0.5  # Depressed by > 0.5m

    # TWI proxy: ln(a / tan(beta))
    # where a is approximate upslope contributing area proxy (m^2/m)
    tan_beta = max(math.tan(slope_rad), 0.001)
    a_proxy = 100.0  # nominal contributing width
    twi_proxy = math.log(a_proxy / tan_beta)

    return {
        "elevation_m": round(elevation_m, 2),
        "slope_deg": round(slope_deg, 2),
        "slope_pct": round(slope_pct, 2),
        "depression_index": round(max(0.0, depression_drop), 2),
        "is_depression": is_depression,
        "twi_proxy": round(twi_proxy, 2)
    }
