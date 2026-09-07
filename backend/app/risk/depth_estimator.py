from typing import Dict, Any

def estimate_water_depth(
    ponding_depth_m: float,
    is_depression: bool = False,
    depression_drop_m: float = 0.0
) -> Dict[str, Any]:
    """
    Estimates water depth bracket based on hydrological runoff accumulation and depression geometry.
    
    IMPORTANT:
    Output is strictly tagged as 'MODEL ESTIMATE' to distinguish it from measured sensor observations.
    Brackets:
      - < 0.10 m (Ankle depth / minor sheet flow)
      - 0.10 - 0.30 m (Curb height / passable by heavy vehicles)
      - 0.30 - 0.50 m (Exhaust level / small cars stranded)
      - 0.50 - 1.00 m (Severe inundation / vehicles submerged)
      - > 1.00 m (Extreme hazard / rapid rescue required)
    """
    effective_depth = max(0.0, ponding_depth_m)
    if is_depression:
        effective_depth += (depression_drop_m * 0.4)

    if effective_depth < 0.10:
        bracket = "< 0.10 m"
    elif effective_depth < 0.30:
        bracket = "0.10-0.30 m"
    elif effective_depth < 0.50:
        bracket = "0.30-0.50 m"
    elif effective_depth < 1.00:
        bracket = "0.50-1.00 m"
    else:
        bracket = "> 1.00 m"

    return {
        "estimated_depth_m": round(effective_depth, 2),
        "estimated_depth_bracket": bracket,
        "provenance_tag": "MODEL_ESTIMATE",
        "description": "Calculated hydrological inundation depth based on SCS-CN runoff accumulation and terrain depression geometry."
    }
