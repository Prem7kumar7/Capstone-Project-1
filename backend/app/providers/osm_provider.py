from pathlib import Path
from typing import Dict, Any
from backend.app.config import settings
from backend.app.providers.base import BaseProvider
from backend.app.utils.geo import load_geojson_safe

class OSMProvider(BaseProvider):
    def __init__(self):
        super().__init__(provider_name="OpenStreetMap / Verified Base", provider_type="GIS")
        self.boundary_file = settings.STUDY_AREAS_DIR / "lpu_osm_boundary.geojson"
        self.nh44_file = settings.STUDY_AREAS_DIR / "nh44_osm_trunk.geojson"

    async def check_health(self) -> Dict[str, Any]:
        boundary_exists = self.boundary_file.exists()
        nh44_exists = self.nh44_file.exists()
        if boundary_exists and nh44_exists:
            self.last_status = "ONLINE"
            self.last_latency_ms = 1.0
            return {
                "status": "ONLINE",
                "provider": self.provider_name,
                "verified_layers": ["lpu_osm_boundary", "nh44_osm_trunk"],
                "drainage_data_status": "NOT_AVAILABLE_UNVERIFIED",
                "infrastructure_status": "NO_UNVERIFIED_ASSETS_INVENTED"
            }
        else:
            self.last_status = "DEGRADED"
            return {"status": "DEGRADED", "missing_layers": [str(self.boundary_file), str(self.nh44_file)]}

    def get_study_area_boundary(self) -> Dict[str, Any]:
        return load_geojson_safe(self.boundary_file)

    def get_road_network(self) -> Dict[str, Any]:
        return load_geojson_safe(self.nh44_file)

    def get_drainage_status(self) -> Dict[str, Any]:
        return {
            "drainage_data_availability": "NOT_AVAILABLE",
            "modelling_mode": "TERRAIN_AND_LAND_COVER_SUSCEPTIBILITY",
            "message": "Sub-surface pipe invert, culvert, and manhole data for LPU campus is currently unverified. The system operates in Terrain + Land-Cover Runoff Susceptibility mode to prevent false hydraulic claims."
        }

osm_provider = OSMProvider()
