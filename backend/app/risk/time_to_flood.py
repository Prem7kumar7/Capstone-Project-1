from typing import Dict, Any

def calculate_estimated_time_to_flood(
    rainfall_intensity_mm_h: float,
    current_depth_m: float,
    threshold_depth_m: float = 0.15,
    is_depression: bool = False
) -> Dict[str, Any]:
    """
    Calculates estimated time-to-flood based on rainfall accumulation rate and conveyance capacity.
    
    IMPORTANT:
    Output is strictly tagged as 'ESTIMATED'. Never displayed as an exact time.
    Brackets:
      - 0-30 min
      - 30-60 min
      - 1-2 hours
      - 2-4 hours
      - 4-6 hours
      - > 6 hours / Low Risk
    """
    if rainfall_intensity_mm_h <= 1.0 and current_depth_m < 0.05:
        return {
            "estimated_time_to_flood": "> 6 hours / Low Risk",
            "time_minutes_approx": None,
            "provenance_tag": "ESTIMATED",
            "urgency": "NONE"
        }

    # If depth already exceeds threshold
    if current_depth_m >= threshold_depth_m:
        return {
            "estimated_time_to_flood": "0-30 min (Active Inundation)",
            "time_minutes_approx": 10,
            "provenance_tag": "ESTIMATED",
            "urgency": "IMMINENT"
        }

    # Estimated rate of rise (m/hr)
    # 50 mm/h rain on high impervious ground creates ~0.04m ponding per hour
    rate_of_rise_m_h = (rainfall_intensity_mm_h / 1000.0) * (1.8 if is_depression else 0.8)
    needed_rise_m = max(0.01, threshold_depth_m - current_depth_m)

    hours_to_threshold = needed_rise_m / max(rate_of_rise_m_h, 0.005)

    if hours_to_threshold <= 0.5:
        bracket = "0-30 min"
        urgency = "IMMINENT"
    elif hours_to_threshold <= 1.0:
        bracket = "30-60 min"
        urgency = "HIGH"
    elif hours_to_threshold <= 2.0:
        bracket = "1-2 hours"
        urgency = "MODERATE"
    elif hours_to_threshold <= 4.0:
        bracket = "2-4 hours"
        urgency = "LOW"
    elif hours_to_threshold <= 6.0:
        bracket = "4-6 hours"
        urgency = "LOW"
    else:
        bracket = "> 6 hours"
        urgency = "NONE"

    return {
        "estimated_time_to_flood": bracket,
        "time_minutes_approx": round(hours_to_threshold * 60, 0),
        "provenance_tag": "ESTIMATED",
        "urgency": urgency
    }
