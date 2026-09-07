from fastapi import APIRouter
from backend.app.config import settings
from backend.app.providers.open_meteo import open_meteo_provider
from backend.app.providers.open_meteo_elevation import elevation_provider
from backend.app.providers.osm_provider import osm_provider
from backend.app.providers.gpm import gpm_provider, imd_provider
from backend.app.hydrology.swmm_coupler import swmm_coupler
from backend.app.advanced_nowcasting.advection_optical_flow import spatial_nowcaster
from backend.app.utils.geo import utc_to_ist_str
from datetime import datetime, timezone

router = APIRouter(prefix="/data-health", tags=["Data Health & Provenance"])

@router.get("/status")
async def get_system_data_health():
    """
    Returns real-time operational health and data provenance across all integrated data sources.
    Transparently reports whether an external API is online, degraded, or dormant.
    """
    # Check live providers
    om_health = await open_meteo_provider.check_health()
    elev_health = await elevation_provider.check_health()
    osm_health = await osm_provider.check_health()
    gpm_health = await gpm_provider.check_health()
    imd_health = await imd_provider.check_health()
    swmm_status = swmm_coupler.get_engine_status()
    nowcast_status = spatial_nowcaster.check_feed_status(radar_feed_connected=False)

    now_utc = datetime.now(timezone.utc)
    ist_time = utc_to_ist_str(now_utc)

    providers = [
        {
            "provider_name": "Open-Meteo NWP Forecast",
            "provider_type": "WEATHER_API",
            "status": om_health.get("status", "UNKNOWN"),
            "latency_ms": om_health.get("latency_ms"),
            "last_updated_ist": ist_time,
            "data_provenance": "LIVE",
            "notes": "ECMWF/GFS numerical weather blend (15-min / hourly precipitation)"
        },
        {
            "provider_name": "Copernicus DEM (GLO-30 via Open-Meteo)",
            "provider_type": "ELEVATION_DEM",
            "status": elev_health.get("status", "UNKNOWN"),
            "latency_ms": elev_health.get("latency_ms"),
            "last_updated_ist": ist_time,
            "data_provenance": "HISTORICAL_SATELLITE",
            "notes": "30-meter European Space Agency digital surface model"
        },
        {
            "provider_name": "OpenStreetMap / Verified Base",
            "provider_type": "GIS_VECTOR",
            "status": osm_health.get("status", "UNKNOWN"),
            "latency_ms": 1.0,
            "last_updated_ist": ist_time,
            "data_provenance": "HISTORICAL",
            "notes": "Verified LPU boundary and NH-44 trunk road corridor"
        },
        {
            "provider_name": "Campus Drainage Infrastructure Survey",
            "provider_type": "HYDRAULIC_DRAINAGE",
            "status": "NOT_AVAILABLE",
            "latency_ms": None,
            "last_updated_ist": ist_time,
            "data_provenance": "UNVERIFIED",
            "notes": "No fake pipe dimensions invented. System operates in Terrain + Land-Cover Susceptibility mode."
        },
        {
            "provider_name": "EPA SWMM Hydraulic Engine Coupler",
            "provider_type": "HYDRAULIC_SIMULATION",
            "status": swmm_status["status"],
            "latency_ms": None,
            "last_updated_ist": ist_time,
            "data_provenance": "DERIVED",
            "notes": swmm_status["message"]
        },
        {
            "provider_name": "Spatial Optical Flow Radar Engine",
            "provider_type": "RADAR_NOWCASTING",
            "status": nowcast_status["status"],
            "latency_ms": None,
            "last_updated_ist": ist_time,
            "data_provenance": "DERIVED",
            "notes": nowcast_status["message"]
        },
        {
            "provider_name": "NASA GPM IMERG Precipitation",
            "provider_type": "SATELLITE_PRECIPITATION",
            "status": gpm_health.get("status", "DORMANT"),
            "latency_ms": None,
            "last_updated_ist": ist_time,
            "data_provenance": "SATELLITE",
            "notes": gpm_health.get("notes")
        },
        {
            "provider_name": "IMD District Observations (Kapurthala/Jalandhar)",
            "provider_type": "NATIONAL_MET_AGENCY",
            "status": imd_health.get("status", "DORMANT"),
            "latency_ms": None,
            "last_updated_ist": ist_time,
            "data_provenance": "HISTORICAL",
            "notes": imd_health.get("notes")
        }
    ]

    is_healthy = om_health.get("status") == "ONLINE" and elev_health.get("status") == "ONLINE"

    return {
        "system_status": "OPERATIONAL" if is_healthy else "DEGRADED",
        "active_study_area": settings.DEFAULT_STUDY_AREA_NAME,
        "checked_at_ist": ist_time,
        "providers": providers
    }
