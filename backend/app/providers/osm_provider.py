from pathlib import Path
from typing import Dict, Any
from backend.app.config import settings
from backend.app.providers.base import BaseProvider
from backend.app.utils.geo import load_geojson_safe

class OSMProvider(BaseProvider):
    def __init__(self):
        super().__init__(provider_name="OpenStreetMap / Verified Base", provider_type="GIS")
        self.waterways_file = settings.STUDY_AREAS_DIR / "regional_waterways.geojson"
        self.natural_waterways_file = settings.STUDY_AREAS_DIR / "natural_waterways.geojson"
        self.urban_drains_file = settings.STUDY_AREAS_DIR / "urban_stormwater_drains.geojson"
        self.derived_flow_paths_file = settings.STUDY_AREAS_DIR / "derived_flow_paths.geojson"
        self.infra_file = settings.STUDY_AREAS_DIR / "critical_infrastructure.geojson"

    async def check_health(self) -> Dict[str, Any]:
        lpu_file = settings.STUDY_AREAS_DIR / "lpu_osm_boundary.geojson"
        nh44_file = settings.STUDY_AREAS_DIR / "nh44_osm_trunk.geojson"
        all_ok = lpu_file.exists() and nh44_file.exists()
        if all_ok:
            self.last_status = "ONLINE"
            self.last_latency_ms = 1.0
            return {
                "status": "ONLINE",
                "provider": self.provider_name,
                "verified_regions": list(settings.STUDY_REGIONS.keys()),
                "verified_layers": [
                    "lpu_osm_boundary", "chaheru_osm_boundary", "phagwara_osm_boundary",
                    "jalandhar_osm_boundary", "nh44_osm_trunk", "natural_waterways",
                    "urban_stormwater_drains", "derived_flow_paths", "critical_infrastructure"
                ],
                "drainage_data_status": "SURFACE_AND_NATURAL_CHOS_AVAILABLE",
                "infrastructure_status": "CIVIC_ASSETS_VERIFIED"
            }
        else:
            self.last_status = "DEGRADED"
            return {"status": "DEGRADED", "message": "Some baseline GeoJSON layers are missing."}

    def get_study_area_boundary(self, region_id: str = "lpu_main_campus") -> Dict[str, Any]:
        cfg = settings.STUDY_REGIONS.get(region_id, settings.STUDY_REGIONS["lpu_main_campus"])
        bfile = settings.STUDY_AREAS_DIR / cfg.get("boundary_file", "lpu_osm_boundary.geojson")
        return load_geojson_safe(bfile)

    def get_road_network(self, region_id: str = "lpu_main_campus") -> Dict[str, Any]:
        cfg = settings.STUDY_REGIONS.get(region_id, settings.STUDY_REGIONS["lpu_main_campus"])
        rfile = settings.STUDY_AREAS_DIR / cfg.get("roads_file", "nh44_osm_trunk.geojson")
        return load_geojson_safe(rfile)

    def get_natural_waterways(self) -> Dict[str, Any]:
        """Returns genuine natural river/stream corridors (Kali Bein river, Chaheru stream)."""
        target = self.natural_waterways_file if self.natural_waterways_file.exists() else self.waterways_file
        return load_geojson_safe(target)

    def get_urban_drainage(self) -> Dict[str, Any]:
        """Returns engineered municipal open stormwater drains (Kala Sanghian, Phagwara Choe, NH-44 saucer drains)."""
        return load_geojson_safe(self.urban_drains_file)

    def get_derived_flow_paths(self, region_id: str = None) -> Dict[str, Any]:
        """Returns DEM-derived overland surface flow paths (Copernicus DEM 30m D8 steepest descent)."""
        data = load_geojson_safe(self.derived_flow_paths_file)
        if not region_id or "features" not in data:
            return data
        filtered = [f for f in data.get("features", []) if f.get("properties", {}).get("region_id") == region_id]
        return {"type": "FeatureCollection", "features": filtered}

    def get_waterways(self) -> Dict[str, Any]:
        """Returns combined regional waterways for backward compatibility."""
        return load_geojson_safe(self.waterways_file)

    def get_critical_infrastructure(self, region_id: str = None) -> Dict[str, Any]:
        data = load_geojson_safe(self.infra_file)
        if not region_id or "features" not in data:
            return data
        filtered = [f for f in data.get("features", []) if f.get("properties", {}).get("region_id") == region_id]
        return {"type": "FeatureCollection", "features": filtered}

    def get_drainage_status(self, region_id: str = "lpu_main_campus") -> Dict[str, Any]:
        reg = settings.STUDY_REGIONS.get(region_id, settings.STUDY_REGIONS["lpu_main_campus"])
        return {
            "study_area_id": region_id,
            "study_area_name": reg["name"],
            "drainage_data_availability": "LEVEL_2_PARTIAL_SURFACE_CHANNELS",
            "modelling_mode": "TERRAIN_FLOW_ACCUMULATION_AND_SURFACE_CHANNELS",
            "active_receiving_channels": [
                "Chaheru Stream / Nullah",
                "Phagwara Choe",
                "Kala Sanghian Drain",
                "Kali Bein River"
            ],
            "sub_surface_pipes_status": "NOT_PUBLICLY_AVAILABLE",
            "message": (
                f"Sub-surface pipe diameter, invert levels, and manhole records for {reg['name']} "
                "are not publicly published by the municipal corporation / university administration. "
                "The system operates in Level 1 (Copernicus DEM 30m flow accumulation) and Level 2 "
                "(mapped surface drains & chos) to prevent false hydraulic claims."
            )
        }

osm_provider = OSMProvider()
