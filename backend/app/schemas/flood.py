from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class FloodHotspotResponse(BaseModel):
    id: int
    location_name: str
    latitude: float
    longitude: float
    elevation_m: Optional[float] = None
    flood_risk_score: float = Field(..., ge=0.0, le=100.0, description="Composite Flood Risk Score (0-100), uncalibrated index")
    risk_category: str  # VERY_LOW, LOW, MODERATE, HIGH, EXTREME
    estimated_depth_bracket: str  # < 0.10 m, 0.10-0.30 m, etc.
    estimated_depth_label: str = "MODEL ESTIMATE"
    estimated_time_to_flood: str  # 0-30 min, 30-60 min, etc.
    estimated_time_label: str = "ESTIMATED"
    susceptibility_factors: Optional[Dict[str, Any]] = None
    data_provenance: str

class FloodPredictionRunResponse(BaseModel):
    run_id: str
    study_area_id: str
    run_timestamp_utc: str
    run_timestamp_ist: str
    execution_mode: str  # LIVE, SIMULATED
    modelling_mode: str  # TERRAIN_RUNOFF_SUSCEPTIBILITY, SIMPLIFIED_RUNOFF_LIMITATION, SWMM_HYDRAULIC
    current_rainfall_mm_h: float
    forecast_cumulative_6h_mm: float
    max_forecast_intensity_mm_h: float
    drainage_clogging_fraction: float
    max_flood_risk_score: float = Field(..., ge=0.0, le=100.0)
    overall_severity: str
    highest_estimated_depth_bracket: str
    earliest_time_to_flood: str
    affected_hotspots_count: int
    confidence_level: str  # HIGH, MEDIUM, LOW
    data_sources: List[str]
    model_version: str
    is_simulation: bool
    hotspots: List[FloodHotspotResponse]

class LocationInspectionRequest(BaseModel):
    latitude: float
    longitude: float
    study_area_id: Optional[str] = "lpu_main_campus"

class LocationInspectionResponse(BaseModel):
    latitude: float
    longitude: float
    location_label: str
    elevation_m: float
    slope_deg: float
    land_cover_type: str
    curve_number: int
    current_rainfall_mm_h: float
    forecast_cumulative_6h_mm: float
    runoff_depth_mm: float
    flood_risk_score: float = Field(..., ge=0.0, le=100.0)
    risk_category: str
    estimated_depth_bracket: str
    estimated_depth_label: str = "MODEL ESTIMATE"
    estimated_time_to_flood: str
    estimated_time_label: str = "ESTIMATED"
    data_source: str
    provenance: str
    confidence: str
    updated_at_ist: str
