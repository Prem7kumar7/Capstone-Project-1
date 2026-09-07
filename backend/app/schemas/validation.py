from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ValidationEventCreate(BaseModel):
    study_area_id: str = "lpu_main_campus"
    location_name: str
    latitude: float
    longitude: float
    observed_rainfall_24h_mm: float
    peak_intensity_mm_h: Optional[float] = None
    lead_time_hours: float
    predicted_risk_score: float
    predicted_risk_category: str
    predicted_depth_bracket: str
    predicted_depth_m: Optional[float] = None
    observed_flooded: bool
    observed_depth_m: Optional[float] = None
    observed_depth_bracket: Optional[str] = None
    ground_truth_source: str
    notes: Optional[str] = None
    verified_by: Optional[str] = None

class ValidationEventResponse(BaseModel):
    id: str
    event_timestamp_utc: str
    location_name: str
    coordinates: List[float]
    observed_rainfall_24h_mm: float
    predicted_risk_score: float
    observed_flooded: bool
    predicted_depth_bracket: str
    observed_depth_bracket: Optional[str]
    ground_truth_source: str
    status: str

class ValidationMetricsResponse(BaseModel):
    validation_status: str  # INSUFFICIENT_GROUND_TRUTH, PARTIALLY_VALIDATED, VALIDATED
    total_events_recorded: int
    message: str
    metrics: Optional[Dict[str, Any]] = None
    events: List[ValidationEventResponse] = []
