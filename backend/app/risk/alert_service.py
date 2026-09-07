import uuid
from typing import Dict, Any, List
from datetime import datetime, timezone
from backend.app.utils.geo import utc_to_ist_str

def generate_alert_advisory(
    study_area_id: str,
    location_name: str,
    flood_risk_score: float,
    current_rainfall_intensity_mm_h: float,
    forecast_cumulative_6h_mm: float,
    estimated_depth_bracket: str,
    estimated_time_to_flood: str,
    data_source: str,
    is_simulation: bool = False
) -> Dict[str, Any]:
    """
    Evaluates risk thresholds and formats standardized disaster management advisories.
    Alert Levels:
      - GREEN: Normal / Monitoring
      - YELLOW: Watch / Minor waterlogging possible
      - ORANGE: Warning / High flood risk, low-lying road hazard
      - RED: Danger / Extreme flood risk, imminent inundation
    """
    now_utc = datetime.now(timezone.utc)
    issued_ist = utc_to_ist_str(now_utc)
    alert_id = f"ALT-{now_utc.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    # Determine Alert Level based on engineering composite score & rainfall
    if flood_risk_score >= 80.0 or (forecast_cumulative_6h_mm >= 100.0 and flood_risk_score >= 70.0):
        level = "RED"
        headline = f"CRITICAL FLOOD RISK WARNING: {location_name}"
        recommendations = (
            "1. Avoid low-lying underpasses and roads immediately.\n"
            "2. Restrict vehicular movement across NH-44 access underpass.\n"
            "3. University security: Divert traffic towards Gate 2 / Chaheru elevated access.\n"
            "4. Facilities: Verify stormwater pumps are operational.\n"
            "5. Monitor local district administration (Kapurthala/Jalandhar) emergency channels."
        )
    elif flood_risk_score >= 60.0 or (forecast_cumulative_6h_mm >= 60.0 and flood_risk_score >= 50.0):
        level = "ORANGE"
        headline = f"FLOOD ADVISORY (HIGH RISK): {location_name}"
        recommendations = (
            "1. Exercise caution near open roadside swales and campus drainage corridors.\n"
            "2. Slow down driving on NH-44 Grand Trunk Road.\n"
            "3. Relocate sensitive equipment on ground floors to elevated platforms.\n"
            "4. Keep campus emergency assembly lawns accessible."
        )
    elif flood_risk_score >= 35.0:
        level = "YELLOW"
        headline = f"FLOOD WATCH: {location_name}"
        recommendations = (
            "1. Routine weather watch active. Localized puddles expected on paved areas.\n"
            "2. University maintenance to inspect grates and roadside ditch inlets for debris."
        )
    else:
        level = "GREEN"
        headline = f"NORMAL CONDITIONS: {location_name}"
        recommendations = "All drainage corridors operating normally. No immediate flood threat detected."

    provenance = "SIMULATED" if is_simulation else "LIVE"

    return {
        "id": alert_id,
        "study_area_id": study_area_id,
        "alert_level": level,
        "headline": headline,
        "location_name": location_name,
        "forecast_rainfall_summary": f"Current: {current_rainfall_intensity_mm_h:.1f} mm/h | 6h Accumulation: {forecast_cumulative_6h_mm:.1f} mm",
        "flood_risk_score": flood_risk_score,
        "estimated_depth_bracket": estimated_depth_bracket,
        "estimated_time_to_impact": estimated_time_to_flood,
        "recommended_actions": recommendations,
        "data_source": data_source,
        "provenance": provenance,
        "issued_at_ist": issued_ist,
        "is_simulation": is_simulation
    }
