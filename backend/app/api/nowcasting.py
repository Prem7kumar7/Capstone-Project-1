from fastapi import APIRouter
from backend.app.providers.open_meteo import open_meteo_provider
from backend.app.nowcasting.persistence import PersistenceModel
from backend.app.nowcasting.trend import TrendExtrapolationModel
from backend.app.advanced_nowcasting.advection_optical_flow import spatial_nowcaster
from backend.app.advanced_nowcasting.convlstm_interface import convlstm_spec

router = APIRouter(prefix="/nowcasting", tags=["0-6h Rainfall Nowcasting"])

persistence_model = PersistenceModel()
trend_model = TrendExtrapolationModel()

@router.get("/compare")
async def compare_nowcast_models():
    """
    Compares 0-6 hour rainfall nowcasting models:
    - NWP Forecast (Open-Meteo)
    - Persistence Decay Baseline
    - Statistical Trend Extrapolation
    """
    weather = await open_meteo_provider.get_current_and_forecast()
    current_int = weather.get("precipitation_mm_h", 0.0)
    hourly = weather.get("hourly_forecast", [])
    history = [h.get("precipitation_mm", 0.0) for h in hourly[:3]]

    horizons = [0.5, 1.0, 2.0, 3.0, 4.0, 6.0]
    comparison = []

    for h in horizons:
        p_res = persistence_model.predict(current_int, history, h)
        t_res = trend_model.predict(current_int, history, h)
        
        # Approximate matching NWP hourly step
        nwp_idx = min(int(round(h)), len(hourly) - 1)
        nwp_val = hourly[nwp_idx].get("precipitation_mm", 0.0) if hourly else 0.0

        comparison.append({
            "lead_time_hours": h,
            "nwp_forecast_mm_h": nwp_val,
            "persistence_model_mm_h": p_res["projected_intensity_mm_h"],
            "trend_model_mm_h": t_res["projected_intensity_mm_h"],
            "persistence_confidence": p_res["confidence_score"],
            "trend_confidence": t_res["confidence_score"]
        })

    return {
        "current_observation_mm_h": current_int,
        "lead_time_comparison": comparison,
        "active_models": [
            {"name": persistence_model.model_name, "category": "NWP_PERSISTENCE_BASELINE"},
            {"name": trend_model.model_name, "category": "NWP_STATISTICAL_TREND"}
        ]
    }

@router.get("/advanced-status")
def get_advanced_spatial_status():
    """
    Returns the status of the dedicated Advanced Spatial Nowcasting module (Optical Flow & Deep Learning).
    Exposes input data prerequisites (Doppler radar / Satellite grids).
    """
    opt_flow_status = spatial_nowcaster.check_feed_status(radar_feed_connected=False)
    dl_status = convlstm_spec.get_prerequisites()

    return {
        "optical_flow_module": opt_flow_status,
        "deep_learning_convlstm_module": dl_status,
        "summary": "Advanced spatial modules are architecturally ready. Awaiting live Doppler Weather Radar CAPPI polar volume ingestion."
    }

@router.get("/timeline")
async def get_nowcasting_timeline(study_area_id: str = "lpu_main_campus"):
    """
    Generates a continuous 0-6 hour nowcast timeline across 8 discrete horizons:
    +0m (Now), +15m, +30m, +1h, +2h, +3h, +4h, +5h, +6h.
    Computes both projected rainfall and corresponding simulated/nowcasted flood risk.
    """
    from backend.app.config import settings
    from backend.app.risk.pipeline_service import execute_nowcasting_pipeline

    region = settings.STUDY_REGIONS.get(study_area_id, settings.STUDY_REGIONS["lpu_main_campus"])
    weather = await open_meteo_provider.get_current_and_forecast(
        lat=region["centroid"]["lat"],
        lon=region["centroid"]["lon"]
    )
    current_int = weather.get("precipitation_mm_h", 0.0)
    hourly = weather.get("hourly_forecast", [])
    history = [h.get("precipitation_mm", 0.0) for h in hourly[:3]]

    horizons = [
        {"lead_hours": 0.0, "label": "Now (0h)"},
        {"lead_hours": 0.25, "label": "+15 min"},
        {"lead_hours": 0.5, "label": "+30 min"},
        {"lead_hours": 1.0, "label": "+1 hour"},
        {"lead_hours": 2.0, "label": "+2 hours"},
        {"lead_hours": 3.0, "label": "+3 hours"},
        {"lead_hours": 4.0, "label": "+4 hours"},
        {"lead_hours": 5.0, "label": "+5 hours"},
        {"lead_hours": 6.0, "label": "+6 hours"}
    ]

    timeline_points = []
    for h in horizons:
        lead = h["lead_hours"]
        if lead == 0.0:
            proj_mm_h = current_int
            conf = 0.95
        else:
            t_pred = trend_model.predict(current_int, history, lead)
            proj_mm_h = t_pred["projected_intensity_mm_h"]
            conf = t_pred["confidence_score"]

        # Fast risk calculation for horizon
        run_res = await execute_nowcasting_pipeline(
            study_area_id=study_area_id,
            lead_time_hours=lead,
            is_simulation=False
        )

        timeline_points.append({
            "lead_time_hours": lead,
            "label": h["label"],
            "projected_rainfall_mm_h": round(proj_mm_h, 1),
            "confidence_score": conf,
            "max_flood_risk_score": run_res["max_flood_risk_score"],
            "overall_severity": run_res["overall_severity"],
            "highest_estimated_depth_bracket": run_res["highest_estimated_depth_bracket"],
            "affected_hotspots_count": run_res["affected_hotspots_count"],
            "provenance": "OBSERVED" if lead == 0.0 else "NOWCAST_PREDICTION"
        })

    return {
        "study_area_id": study_area_id,
        "study_area_name": region["name"],
        "base_rainfall_mm_h": current_int,
        "forecast_horizons": timeline_points
    }

