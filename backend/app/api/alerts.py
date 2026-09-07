from fastapi import APIRouter
from typing import List
from backend.app.schemas.alert import AlertAdvisoryResponse, AlertThresholdSchema, AlertThresholdUpdate
from backend.app.risk.pipeline_service import execute_nowcasting_pipeline
from backend.app.risk.alert_service import generate_alert_advisory

router = APIRouter(prefix="/alerts", tags=["Emergency Alerts & Advisories"])

# In-memory configurable thresholds
DEFAULT_THRESHOLDS = [
    {"level": "GREEN", "min_rainfall_intensity_mm_h": 0.0, "min_cumulative_rainfall_mm": 0.0, "min_flood_risk_score": 0.0, "description": "Normal conditions / Monitoring mode"},
    {"level": "YELLOW", "min_rainfall_intensity_mm_h": 15.0, "min_cumulative_rainfall_mm": 30.0, "min_flood_risk_score": 35.0, "description": "Watch: Localized minor water accumulation"},
    {"level": "ORANGE", "min_rainfall_intensity_mm_h": 35.0, "min_cumulative_rainfall_mm": 60.0, "min_flood_risk_score": 60.0, "description": "Advisory: High flood risk, underpass caution"},
    {"level": "RED", "min_rainfall_intensity_mm_h": 60.0, "min_cumulative_rainfall_mm": 100.0, "min_flood_risk_score": 80.0, "description": "Warning: Severe inundation threat, road closures"}
]

@router.get("/active")
async def get_active_alerts(is_simulation: bool = False):
    """Generates active location-specific alerts based on latest nowcast."""
    pipeline_res = await execute_nowcasting_pipeline(is_simulation=is_simulation)
    hotspots = pipeline_res.get("hotspots", [])
    
    advisories = []
    for h in hotspots:
        adv = generate_alert_advisory(
            study_area_id=pipeline_res["study_area_id"],
            location_name=h["location_name"],
            flood_risk_score=h["flood_risk_score"],
            current_rainfall_intensity_mm_h=pipeline_res["current_rainfall_mm_h"],
            forecast_cumulative_6h_mm=pipeline_res["forecast_cumulative_6h_mm"],
            estimated_depth_bracket=h["estimated_depth_bracket"],
            estimated_time_to_flood=h["estimated_time_to_flood"],
            data_source="Pipeline Risk Engine (Live NWP / DEM)",
            is_simulation=is_simulation
        )
        advisories.append(adv)

    return advisories

@router.get("/thresholds")
def get_alert_thresholds():
    return DEFAULT_THRESHOLDS

@router.put("/thresholds/{level}")
def update_alert_threshold(level: str, update: AlertThresholdUpdate):
    for t in DEFAULT_THRESHOLDS:
        if t["level"] == level.upper():
            if update.min_rainfall_intensity_mm_h is not None:
                t["min_rainfall_intensity_mm_h"] = update.min_rainfall_intensity_mm_h
            if update.min_cumulative_rainfall_mm is not None:
                t["min_cumulative_rainfall_mm"] = update.min_cumulative_rainfall_mm
            if update.min_flood_risk_score is not None:
                t["min_flood_risk_score"] = update.min_flood_risk_score
            if update.description is not None:
                t["description"] = update.description
            return {"status": "SUCCESS", "updated_threshold": t}
    return {"status": "NOT_FOUND", "message": f"Threshold for {level} not found"}
