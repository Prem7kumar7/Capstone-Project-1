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
