import os
from pathlib import Path
from typing import List
from pydantic import Field
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseModel as BaseSettings

# Resolve base project directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"

class Settings(BaseSettings):
    PROJECT_NAME: str = "Urban Flood Nowcasting System - Lovely Professional University (LPU)"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'flood_nowcasting.db'}")
    
    # Geospatial Multi-Region Configuration
    DEFAULT_STUDY_AREA_ID: str = "lpu_main_campus"
    DEFAULT_STUDY_AREA_NAME: str = "Lovely Professional University & NH-44 Corridor, Phagwara"
    DEFAULT_LAT: float = 31.2533
    DEFAULT_LON: float = 75.7033
    DEFAULT_RADIUS_KM: float = 3.5

    STUDY_REGIONS: dict = {
        "lpu_main_campus": {
            "id": "lpu_main_campus",
            "name": "Lovely Professional University (LPU) Campus",
            "state": "Punjab",
            "district": "Kapurthala",
            "centroid": {"lat": 31.2533, "lon": 75.7033},
            "default_zoom": 16.2,
            "elevation_base_m": 234.0,
            "boundary_file": "lpu_osm_boundary.geojson",
            "roads_file": "nh44_osm_trunk.geojson"
        },
        "chaheru": {
            "id": "chaheru",
            "name": "Chaheru / Chiheru Corridor",
            "state": "Punjab",
            "district": "Kapurthala",
            "centroid": {"lat": 31.2590, "lon": 75.6940},
            "default_zoom": 15.5,
            "elevation_base_m": 232.0,
            "boundary_file": "chaheru_osm_boundary.geojson",
            "roads_file": "nh44_osm_trunk.geojson"
        },
        "phagwara_urban": {
            "id": "phagwara_urban",
            "name": "Phagwara Municipal Basin",
            "state": "Punjab",
            "district": "Kapurthala",
            "centroid": {"lat": 31.2207, "lon": 75.7725},
            "default_zoom": 14.5,
            "elevation_base_m": 249.0,
            "boundary_file": "phagwara_osm_boundary.geojson",
            "roads_file": "nh44_osm_trunk.geojson"
        },
        "jalandhar_metro": {
            "id": "jalandhar_metro",
            "name": "Jalandhar Urban Metro",
            "state": "Punjab",
            "district": "Jalandhar",
            "centroid": {"lat": 31.3260, "lon": 75.5762},
            "default_zoom": 13.5,
            "elevation_base_m": 242.0,
            "boundary_file": "jalandhar_osm_boundary.geojson",
            "roads_file": "nh44_osm_trunk.geojson"
        }
    }
    
    # External APIs
    OPEN_METEO_FORECAST_URL: str = "https://api.open-meteo.com/v1/forecast"
    OPEN_METEO_ELEVATION_URL: str = "https://api.open-meteo.com/v1/elevation"
    OVERPASS_API_URL: str = os.getenv("OVERPASS_API_URL", "https://overpass-api.de/api/interpreter")
    
    # Paths
    BASE_DIR_PATH: Path = BASE_DIR
    DATA_DIR_PATH: Path = DATA_DIR
    STUDY_AREAS_DIR: Path = DATA_DIR / "study_areas"
    SAMPLE_EVENTS_DIR: Path = DATA_DIR / "sample_events"
    
    # Caching & Quality Control
    CACHE_TTL_SECONDS: int = 900  # 15 minutes cache for weather
    REQUEST_TIMEOUT_SECONDS: float = 12.0
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"
    ]
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "sih-2026-lpu-flood-nowcasting-production-secret-key-change-in-prod")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    model_config = {"case_sensitive": True, "env_file": ".env", "extra": "ignore"}

settings = Settings()
