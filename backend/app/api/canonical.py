"""
Canonical REST API Endpoints for SIH26085 Urban Flood Nowcasting System.
Provides top-level routes mandated by the scientific integrity audit:
GET /regions
GET /rainfall
GET /forecast
GET /nowcast
GET /terrain
GET /flood-risk
GET /flood-susceptibility
GET /waterways
GET /drainage
GET /validation
GET /provenance
"""

from fastapi import APIRouter, Query
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import json

from backend.app.config import settings
from backend.app.providers.osm_provider import osm_provider
from backend.app.providers.open_meteo import open_meteo_provider
from backend.app.risk.pipeline_service import execute_nowcasting_pipeline
from backend.app.api.nowcasting import get_nowcasting_timeline
from backend.app.api.validation import get_validation_metrics, get_historical_satellite_events
from backend.app.utils.geo import utc_to_ist_str, load_geojson_safe

router = APIRouter(tags=["Canonical SIH26085 Endpoints"])

@router.get("/regions")
def get_all_regions():
    """
    Returns all 4 geographically and hydrologically distinct study regions
    (LPU Campus, Chaheru, Phagwara, Jalandhar) with full metadata and data status.
    """
    regions_list = []
    for reg_id, reg in settings.STUDY_REGIONS.items():
        drain_status = osm_provider.get_drainage_status(reg_id)
        regions_list.append({
            "id": reg["id"],
            "name": reg["name"],
            "state": reg["state"],
            "district": reg["district"],
            "centroid": reg["centroid"],
            "default_zoom": reg["default_zoom"],
            "elevation_base_m": reg["elevation_base_m"],
            "boundary_file": reg.get("boundary_file"),
            "roads_file": reg.get("roads_file"),
            "drainage_availability": drain_status["drainage_data_availability"],
            "sub_surface_pipes": drain_status["sub_surface_pipes_status"],
            "status": "ACTIVE"
        })
    return {
        "status": "AVAILABLE",
        "total_regions": len(regions_list),
        "study_regions": regions_list,
        "provenance": "VERIFIED_GEOSPATIAL_BOUNDARIES"
    }

@router.get("/rainfall")
async def get_rainfall_with_hierarchy(lat: Optional[float] = None, lon: Optional[float] = None):
    """
    Returns standardized rainfall record with strict source hierarchy:
    PRIMARY: IMD (Restricted / MoU required)
    SECONDARY: NASA GPM IMERG (Available / Token required)
    FALLBACK: Open-Meteo NWP ECMWF/GFS Blend (Live active operational source)
    """
    data = await open_meteo_provider.get_current_and_forecast(lat=lat, lon=lon)
    now_utc = datetime.now(timezone.utc)
    
    return {
        "timestamp": data.get("timestamp_utc", now_utc.isoformat()),
        "timestamp_ist": data.get("timestamp_ist", utc_to_ist_str(now_utc)),
        "value": data.get("precipitation_mm_h", 0.0),
        "unit": "mm/h",
        "rain_accumulation_mm": data.get("rain_mm", 0.0),
        "source": data.get("data_source", "Open-Meteo Global NWP Model"),
        "source_url": "https://api.open-meteo.com/v1/forecast",
        "status": "LIVE",
        "source_hierarchy": {
            "primary": {
                "source": "India Meteorological Department (IMD)",
                "source_url": "https://mausam.imd.gov.in",
                "status": "RESTRICTED",
                "notes": "Programmatic sub-hourly radar JSON streaming requires departmental MoU"
            },
            "secondary": {
                "source": "NASA GPM IMERG (Early/Late)",
                "source_url": "https://gpm.nasa.gov/data/imerg",
                "status": "AVAILABLE",
                "notes": "Half-hourly 0.1 deg (~10 km) satellite grid; requires NASA Earthdata auth token for continuous streaming"
            },
            "fallback": {
                "source": "Open-Meteo Global NWP Model (ECMWF/GFS blend)",
                "source_url": "https://api.open-meteo.com/v1/forecast",
                "status": "LIVE_OPERATIONAL_FALLBACK",
                "is_active": True
            }
        }
    }

@router.get("/forecast")
async def get_rainfall_forecast():
    """
    Returns 0-6 hour short-term precipitation forecast baseline (ECMWF/GFS numerical model blend).
    """
    data = await open_meteo_provider.get_current_and_forecast()
    return {
        "issued_at_utc": data["timestamp_utc"],
        "issued_at_ist": data["timestamp_ist"],
        "forecast_horizon_hours": data.get("forecast_horizon_hours", 6),
        "cumulative_forecast_6h_mm": data.get("cumulative_forecast_6h_mm", 0.0),
        "max_forecast_intensity_mm_h": data.get("max_forecast_intensity_mm_h", 0.0),
        "hourly_breakdown": data.get("hourly_forecast", []),
        "source": "Open-Meteo NWP ECMWF/GFS Blend",
        "source_url": "https://api.open-meteo.com/v1/forecast",
        "status": "FORECAST",
        "methodology": "Global numerical weather prediction model grid interpolation"
    }

@router.get("/nowcast")
async def get_nowcast_timeline(study_area_id: str = Query("lpu_main_campus")):
    """
    Returns 0-6 hour short-term nowcast baseline (+15m, +30m, +1h... +6h)
    derived from polynomial-dampened trend extrapolation of NWP precipitation.
    Strictly labeled: BASELINE SHORT-TERM RAINFALL NOWCAST (Awaiting Live Doppler Radar feed).
    """
    timeline = await get_nowcasting_timeline(study_area_id=study_area_id)
    
    return {
        "study_area_id": timeline["study_area_id"],
        "study_area_name": timeline["study_area_name"],
        "system_classification": "BASELINE_SHORT_TERM_RAINFALL_NOWCAST",
        "radar_feed_status": "AWAITING_RADAR_FEED (Patiala/Amritsar DWR)",
        "methodology": "Polynomial-dampened Eulerian trend extrapolation: R(t) = max(0, R0 + (dR/dt)*t / (1 + 0.5*t))",
        "forecast_horizons": timeline["forecast_horizons"],
        "status": "DERIVED"
    }

@router.get("/terrain")
def get_terrain_derivatives(region_id: Optional[str] = Query(None)):
    """
    Returns 4-region Copernicus DEM 30m terrain derivatives:
    elevation statistics, slope gradients, D8 flow direction, flow accumulation nodes, and derived flow paths.
    """
    profile_file = settings.STUDY_AREAS_DIR / "terrain_profiles.json"
    if profile_file.exists():
        profiles = json.loads(profile_file.read_text(encoding="utf-8"))
        if region_id and region_id in profiles.get("regions", {}):
            return profiles["regions"][region_id]
        return profiles
    return {
        "status": "UNAVAILABLE",
        "message": "Terrain profiles file not found on disk."
    }

@router.get("/flood-risk")
async def get_current_flood_risk(
    study_area_id: str = Query("lpu_main_campus"),
    lead_time_hours: float = Query(0.0)
):
    """
    Returns composite Flood Risk Score (0-100) across candidate flood-prone locations.
    Strictly labeled: UNCALIBRATED ENGINEERING RISK INDEX (0-100).
    """
    res = await execute_nowcasting_pipeline(
        study_area_id=study_area_id,
        lead_time_hours=lead_time_hours,
        is_simulation=False
    )
    res["metric_classification"] = "UNCALIBRATED ENGINEERING RISK INDEX (0-100)"
    res["is_statistical_probability"] = False
    return res

@router.get("/flood-susceptibility")
def get_flood_susceptibility(region_id: str = Query("lpu_main_campus")):
    """
    Returns terrain and SCS-CN runoff susceptibility index for the study region.
    """
    profile_file = settings.STUDY_AREAS_DIR / "terrain_profiles.json"
    if profile_file.exists():
        profiles = json.loads(profile_file.read_text(encoding="utf-8"))
        reg = profiles.get("regions", {}).get(region_id)
        if reg:
            return {
                "region_id": region_id,
                "name": reg["name"],
                "land_cover": reg["land_cover"],
                "slope": reg["slope"],
                "flow_accumulation": reg["flow_accumulation"],
                "susceptibility": reg["flood_susceptibility"],
                "status": "DERIVED"
            }
    return {"status": "UNAVAILABLE"}

@router.get("/waterways")
def get_natural_waterways_geojson():
    """
    Returns genuine natural river and stream corridors (Kali Bein river, Chaheru stream).
    Classification: NATURAL_WATERWAY.
    """
    return osm_provider.get_natural_waterways()

@router.get("/drainage")
def get_urban_drainage_geojson():
    """
    Returns engineered municipal open stormwater drains (Kala Sanghian, Phagwara Choe, NH-44 saucer swales).
    Classification: URBAN_STORMWATER_DRAIN.
    Sub-surface pipe network is transparently declared UNAVAILABLE.
    """
    data = osm_provider.get_urban_drainage()
    return data

@router.get("/validation")
def get_satellite_validation_report():
    """
    Returns remote-sensing validation metrics event-by-event across August 2019, August 2020, and July 2023.
    Terminology: SATELLITE-OBSERVED FLOOD EXTENT / REMOTE-SENSING VALIDATION DATA.
    """
    metrics = get_validation_metrics()
    events = get_historical_satellite_events()
    return {
        "validation_type": "REMOTE_SENSING_VALIDATION_DATA",
        "terminology_note": "Validation utilizes satellite-observed flood extents (Sentinel-1 SAR C-band, NRSC NDEM). It is not synthetic/perfect ground truth.",
        "metrics_summary": metrics,
        "historical_events_catalog": events
    }

@router.get("/provenance")
def get_system_provenance_registry():
    """
    Returns the master data provenance registry for all layers and indicators in the system,
    with explicit status badges: LIVE, FORECAST, HISTORICAL, DERIVED, ESTIMATED, ASSUMED, SIMULATED, UNAVAILABLE, RESTRICTED.
    """
    return {
        "provenance_registry_version": "1.0.0",
        "last_audit_utc": datetime.now(timezone.utc).isoformat(),
        "datasets": [
            {
                "layer_name": "Open-Meteo NWP Forecast",
                "source": "Open-Meteo / ECMWF / GFS",
                "source_url": "https://api.open-meteo.com/v1/forecast",
                "status": "LIVE",
                "units": "mm/h, Celsius, %",
                "resolution": "Hourly, ~10 km"
            },
            {
                "layer_name": "India Meteorological Dept (IMD) Radar/AWS",
                "source": "IMD Mausam / DWR Patiala",
                "source_url": "https://mausam.imd.gov.in",
                "status": "RESTRICTED",
                "notes": "Sub-hourly radar JSON feeds require formal departmental MoU"
            },
            {
                "layer_name": "NASA GPM IMERG Satellite Precipitation",
                "source": "NASA Earthdata DAAC",
                "source_url": "https://gpm.nasa.gov/data/imerg",
                "status": "AVAILABLE",
                "resolution": "0.1 deg (~10 km), 30-min latency"
            },
            {
                "layer_name": "Copernicus DEM Elevation GLO-30",
                "source": "Copernicus Space Component / ESA",
                "source_url": "https://spacedata.copernicus.eu",
                "status": "AVAILABLE",
                "resolution": "30 meters",
                "crs": "EPSG:4326"
            },
            {
                "layer_name": "ESA WorldCover 10m Land Cover",
                "source": "European Space Agency (ESA) Open Data",
                "source_url": "https://esa-worldcover.org",
                "status": "AVAILABLE",
                "resolution": "10 meters",
                "tile": "N30E075"
            },
            {
                "layer_name": "OpenStreetMap Geographic Baselines",
                "source": "OpenStreetMap Contributors (ODbL)",
                "source_url": "https://www.openstreetmap.org",
                "status": "AVAILABLE",
                "layers": "Boundaries, Roads (NH-44), Waterways, Critical Infrastructure"
            },
            {
                "layer_name": "Sub-Surface Municipal Storm Sewer Pipe Drawings",
                "source": "Municipal Corporation Jalandhar / MC Phagwara / LPU Estate",
                "status": "UNAVAILABLE",
                "notes": "Drawings are private municipal records; zero synthetic geometry is invented"
            },
            {
                "layer_name": "Historical Satellite Flood Extents (2019, 2020, 2023)",
                "source": "ISRO / NRSC NDEM & Copernicus Sentinel-1 SAR",
                "status": "HISTORICAL",
                "satellite_bands": "C-SAR VV/VH backscatter (sigma_0 < -15 dB)"
            },
            {
                "layer_name": "Flood Risk Score (0-100)",
                "source": "System Risk Engine (SCS-CN + DEM flow accumulation + Drainage proxy)",
                "status": "DERIVED",
                "nature": "UNCALIBRATED ENGINEERING RISK INDEX (0-100)"
            }
        ]
    }
