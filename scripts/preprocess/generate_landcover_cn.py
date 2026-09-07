"""
Preprocesses ESA WorldCover 10m Land Cover classes and derives
SCS Runoff Curve Numbers (CN) for Hydrologic Soil Group B (Alluvial Silt Loam).
"""
from typing import Dict, Any

# ESA WorldCover 2021 class mappings to SCS Runoff Curve Numbers (HSG B)
ESA_WORLDCOVER_TO_CN_MAP = {
    10: {"label": "Tree Cover", "cn_b": 60, "impervious_pct": 5},
    20: {"label": "Shrubland", "cn_b": 65, "impervious_pct": 10},
    30: {"label": "Grassland / Lawn", "cn_b": 69, "impervious_pct": 15},
    40: {"label": "Cropland (Paddy / Wheat)", "cn_b": 78, "impervious_pct": 20},
    50: {"label": "Built-up / Urban Impervious", "cn_b": 92, "impervious_pct": 85},
    60: {"label": "Bare / Sparse Vegetation", "cn_b": 82, "impervious_pct": 25},
    70: {"label": "Snow and Ice", "cn_b": 100, "impervious_pct": 100},
    80: {"label": "Permanent Water Bodies", "cn_b": 100, "impervious_pct": 100},
    90: {"label": "Herbaceous Wetland", "cn_b": 85, "impervious_pct": 30},
    95: {"label": "Mangroves", "cn_b": 85, "impervious_pct": 30},
    100: {"label": "Moss and Lichen", "cn_b": 75, "impervious_pct": 20}
}

def calculate_scs_cn_parameters(cn: int, lambda_ratio: float = 0.20) -> Dict[str, float]:
    """
    Computes potential maximum soil retention S (mm) and initial abstraction Ia (mm).
    S = (25400 / CN) - 254
    Ia = lambda * S
    """
    if cn <= 0 or cn > 100:
        raise ValueError(f"Invalid Curve Number: {cn}. Must be between 1 and 100.")
    
    if cn == 100:
        s_mm = 0.0
        ia_mm = 0.0
    else:
        s_mm = (25400.0 / float(cn)) - 254.0
        ia_mm = lambda_ratio * s_mm

    return {
        "curve_number": cn,
        "potential_maximum_retention_s_mm": round(s_mm, 2),
        "initial_abstraction_ia_mm": round(ia_mm, 2),
        "lambda_ratio": lambda_ratio
    }

def calculate_direct_runoff_depth(rainfall_p_mm: float, cn: int, lambda_ratio: float = 0.20) -> float:
    """
    Computes SCS-CN direct runoff depth Q (mm):
    Q = (P - Ia)^2 / (P - Ia + S) for P > Ia, else 0.0
    """
    params = calculate_scs_cn_parameters(cn, lambda_ratio)
    ia = params["initial_abstraction_ia_mm"]
    s = params["potential_maximum_retention_s_mm"]

    if rainfall_p_mm <= ia:
        return 0.0

    numerator = (rainfall_p_mm - ia) ** 2
    denominator = rainfall_p_mm - ia + s
    if denominator <= 0:
        return 0.0
    return round(float(numerator / denominator), 2)

if __name__ == "__main__":
    print("=== ESA WorldCover to SCS-CN Parameters (HSG B) ===")
    test_rainfall = 50.0  # mm storm
    for code, info in ESA_WORLDCOVER_TO_CN_MAP.items():
        cn = info["cn_b"]
        params = calculate_scs_cn_parameters(cn, lambda_ratio=0.20)
        q = calculate_direct_runoff_depth(test_rainfall, cn, lambda_ratio=0.20)
        print(f"Code {code:3d} [{info['label']:<30}]: CN={cn:3d} | S={params['potential_maximum_retention_s_mm']:6.1f}mm | Ia={params['initial_abstraction_ia_mm']:5.1f}mm | Runoff Q={q:5.1f}mm (for P={test_rainfall}mm)")
