from fastapi import APIRouter, Query
from typing import Optional
from backend.app.config import settings
from backend.app.providers.osm_provider import osm_provider

router = APIRouter(prefix="/study-area", tags=["Study Area"])

@router.get("")
def get_study_area_info(region_id: Optional[str] = None):
    reg_id = region_id if region_id and region_id in settings.STUDY_REGIONS else settings.DEFAULT_STUDY_AREA_ID
    reg = settings.STUDY_REGIONS[reg_id]
    
    return {
        "study_area_id": reg["id"],
        "name": reg["name"],
        "state": reg["state"],
        "district": reg["district"],
        "centroid": reg["centroid"],
        "default_zoom": reg["default_zoom"],
        "elevation_base_m": reg["elevation_base_m"],
        "available_areas": [
            {
                "id": r["id"],
                "name": r["name"],
                "district": r["district"],
                "centroid": r["centroid"],
                "elevation_base_m": r["elevation_base_m"],
                "status": "ACTIVE"
            }
            for r in settings.STUDY_REGIONS.values()
        ]
    }

@router.get("/boundary")
def get_boundary_geojson(region_id: str = Query("lpu_main_campus")):
    """Returns verified OpenStreetMap boundary polygon for selected study region."""
    return osm_provider.get_study_area_boundary(region_id)

@router.get("/roads")
def get_roads_geojson(region_id: str = Query("lpu_main_campus")):
    """Returns verified road network (NH-44 and connecting roads) for selected study region."""
    return osm_provider.get_road_network(region_id)

@router.get("/waterways")
def get_regional_waterways():
    """Returns verified regional receiving waterways (legacy combined view)."""
    return osm_provider.get_waterways()

@router.get("/natural-waterways")
def get_natural_waterways():
    """Returns verified natural river and stream corridors (Kali Bein river, Chaheru stream)."""
    return osm_provider.get_natural_waterways()

@router.get("/urban-drainage")
def get_urban_drainage():
    """Returns engineered municipal stormwater drains (Kala Sanghian drain, Phagwara Choe, NH-44 saucer drains)."""
    return osm_provider.get_urban_drainage()

@router.get("/infrastructure")
def get_critical_infrastructure(region_id: Optional[str] = None):
    """Returns verified critical civic infrastructure (Hospitals, Emergency services, Transit hubs)."""
    return osm_provider.get_critical_infrastructure(region_id)

@router.get("/drainage-status")
def get_drainage_status(region_id: str = Query("lpu_main_campus")):
    """Returns transparent data status regarding urban sub-surface drainage availability."""
    return osm_provider.get_drainage_status(region_id)

