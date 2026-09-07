from fastapi import APIRouter
from backend.app.config import settings
from backend.app.providers.osm_provider import osm_provider

router = APIRouter(prefix="/study-area", tags=["Study Area"])

@router.get("")
def get_study_area_info():
    return {
        "study_area_id": settings.DEFAULT_STUDY_AREA_ID,
        "name": settings.DEFAULT_STUDY_AREA_NAME,
        "centroid": {"lat": settings.DEFAULT_LAT, "lon": settings.DEFAULT_LON},
        "default_zoom": 15,
        "radius_km": settings.DEFAULT_RADIUS_KM,
        "state": "Punjab",
        "district": "Kapurthala",
        "city": "Phagwara",
        "highway": "NH-44 (Grand Trunk Road)",
        "elevation_base_m": 238.0,
        "available_areas": [
            {"id": "lpu_main_campus", "name": "Lovely Professional University & NH-44 Corridor", "status": "ACTIVE"},
            {"id": "phagwara_urban", "name": "Phagwara Municipal Basin", "status": "CONFIGURABLE"},
            {"id": "jalandhar_metro", "name": "Jalandhar Urban Area", "status": "EXPANSION_READY"}
        ]
    }

@router.get("/boundary")
def get_boundary_geojson():
    """Returns the verified OpenStreetMap boundary polygon for LPU."""
    return osm_provider.get_study_area_boundary()

@router.get("/roads")
def get_roads_geojson():
    """Returns the verified OpenStreetMap road network for NH-44 and campus access."""
    return osm_provider.get_road_network()

@router.get("/drainage-status")
def get_drainage_status():
    """Returns transparent data status regarding campus sub-surface drainage."""
    return osm_provider.get_drainage_status()
