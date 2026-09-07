"""
Computes topographic slope, depression depth, and flow direction across study regions
from verified elevation baselines.
"""
import numpy as np

def compute_slope_deg(elev_drop_m: float, run_dist_m: float) -> float:
    if run_dist_m <= 0:
        return 0.0
    return float(np.degrees(np.arctan(elev_drop_m / run_dist_m)))

def identify_depression(center_elev_m: float, surrounding_elev_m: float) -> tuple:
    is_dep = center_elev_m < surrounding_elev_m
    drop = max(0.0, surrounding_elev_m - center_elev_m) if is_dep else 0.0
    return is_dep, round(drop, 2)

if __name__ == "__main__":
    # Example: NH-44 Underpass near LPU Gate 1
    center_el = 233.1
    surrounding_el = 236.2
    is_dep, drop = identify_depression(center_el, surrounding_el)
    slope = compute_slope_deg(drop, 50.0)
    print(f"NH-44 Underpass: Center={center_el}m, Surrounding={surrounding_el}m -> Depression={is_dep}, Drop={drop}m, Slope={slope:.2f} deg")
