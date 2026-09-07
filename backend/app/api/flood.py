from fastapi import APIRouter
from backend.app.schemas.flood import LocationInspectionRequest, LocationInspectionResponse
from backend.app.risk.pipeline_service import execute_nowcasting_pipeline
from backend.app.providers.open_meteo import open_meteo_provider
from backend.app.providers.open_meteo_elevation import elevation_provider
from backend.app.hydrology.config_loader import hydrology_config_manager
from backend.app.hydrology.scs_cn import calculate_scs_cn_runoff
from backend.app.hydrology.terrain import analyze_terrain_point
from backend.app.risk.risk_engine import calculate_flood_risk_score
from backend.app.risk.depth_estimator import estimate_water_depth
from backend.app.risk.time_to_flood import calculate_estimated_time_to_flood
from backend.app.utils.geo import utc_to_ist_str
from datetime import datetime, timezone

router = APIRouter(prefix="/flood", tags=["Flood Risk & Nowcasting"])

@router.get("/current-risk")
async def get_current_flood_risk():
    """
    Executes the live nowcasting pipeline using real-time weather and DEM inputs.
    Returns composite Flood Risk Scores (0-100), estimated depth brackets, and time-to-flood.
    """
    return await execute_nowcasting_pipeline(is_simulation=False)

@router.post("/inspect-point")
async def inspect_location_point(req: LocationInspectionRequest):
    """
    On-demand GIS point inspection.
    Calculates elevation, slope, SCS-CN runoff, Flood Risk Score (0-100), depth bracket, and time-to-flood.
    """
    # 1. Get elevation for coordinate
    elev_list = await elevation_provider.get_elevation_points([(req.latitude, req.longitude)])
    elev = elev_list[0] if elev_list else 238.0

    # 2. Approximate surrounding elevations for slope
    delta = 0.0003  # ~30m
    surrounding_coords = [
        (req.latitude + delta, req.longitude),
        (req.latitude - delta, req.longitude),
        (req.latitude, req.longitude + delta),
        (req.latitude, req.longitude - delta)
    ]
    surrounding_elevs = await elevation_provider.get_elevation_points(surrounding_coords)
    terrain = analyze_terrain_point(elev, surrounding_elevs, cell_size_m=30.0)

    # 3. Weather
    weather = await open_meteo_provider.get_current_and_forecast(req.latitude, req.longitude)
    curr_int = weather.get("precipitation_mm_h", 0.0)
    cum_6h = weather.get("cumulative_forecast_6h_mm", 0.0)

    # 4. Hydrology
    cn = 85  # Default mixed campus composite
    scs_res = calculate_scs_cn_runoff(cum_6h, cn=cn)

    # 5. Risk Score (0-100)
    risk_res = calculate_flood_risk_score(
        forecast_rainfall_intensity_mm_h=curr_int,
        cumulative_rainfall_mm=cum_6h,
        is_depression=terrain["is_depression"],
        depression_drop_m=terrain["depression_index"],
        slope_deg=terrain["slope_deg"],
        impervious_fraction=0.65,
        drainage_clogging_fraction=0.0,
        drainage_available=False
    )

    # 6. Depth & Time
    depth_res = estimate_water_depth(
        ponding_depth_m=scs_res["runoff_depth_mm"] / 1000.0,
        is_depression=terrain["is_depression"],
        depression_drop_m=terrain["depression_index"]
    )
    time_res = calculate_estimated_time_to_flood(
        rainfall_intensity_mm_h=curr_int,
        current_depth_m=depth_res["estimated_depth_m"],
        is_depression=terrain["is_depression"]
    )

    now_utc = datetime.now(timezone.utc)

    return {
        "latitude": round(req.latitude, 5),
        "longitude": round(req.longitude, 5),
        "location_label": f"Coordinates ({req.latitude:.4f}, {req.longitude:.4f})",
        "elevation_m": round(elev, 1),
        "slope_deg": terrain["slope_deg"],
        "is_depression": terrain["is_depression"],
        "land_cover_type": "campus_mixed_impervious",
        "curve_number": cn,
        "current_rainfall_mm_h": curr_int,
        "forecast_cumulative_6h_mm": cum_6h,
        "runoff_depth_mm": scs_res["runoff_depth_mm"],
        "flood_risk_score": risk_res["flood_risk_score"],
        "risk_category": risk_res["risk_category"],
        "estimated_depth_bracket": depth_res["estimated_depth_bracket"],
        "estimated_depth_label": "MODEL ESTIMATE",
        "estimated_time_to_flood": time_res["estimated_time_to_flood"],
        "estimated_time_label": "ESTIMATED",
        "data_source": "Open-Meteo NWP + Copernicus DEM",
        "provenance": "LIVE_AND_DERIVED",
        "confidence": "MEDIUM",
        "updated_at_ist": utc_to_ist_str(now_utc)
    }
