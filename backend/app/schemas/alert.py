from typing import Optional
from pydantic import BaseModel, Field

class AlertAdvisoryResponse(BaseModel):
    id: str
    study_area_id: str
    alert_level: str  # GREEN, YELLOW, ORANGE, RED
    headline: str
    location_name: str
    forecast_rainfall_summary: str
    flood_risk_score: float
    estimated_depth_bracket: str
    estimated_time_to_impact: str
    recommended_actions: str
    data_source: str
    provenance: str  # LIVE, SIMULATED
    issued_at_ist: str
    is_simulation: bool

class AlertThresholdSchema(BaseModel):
    level: str
    min_rainfall_intensity_mm_h: float
    min_cumulative_rainfall_mm: float
    min_flood_risk_score: float
    description: str

class AlertThresholdUpdate(BaseModel):
    min_rainfall_intensity_mm_h: Optional[float] = None
    min_cumulative_rainfall_mm: Optional[float] = None
    min_flood_risk_score: Optional[float] = None
    description: Optional[str] = None
