from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class CurveNumberItem(BaseModel):
    cn_value: int = Field(..., ge=30, le=100)
    description: str
    impervious_fraction: float = Field(..., ge=0.0, le=1.0)

class HydrologyConfigSchema(BaseModel):
    description: str
    version: str
    provenance: str = "DERIVED_ENGINEERING_STANDARDS"
    references: List[str]
    study_area_id: str
    soil_hydrologic_group: str = Field(..., description="Soil group (A, B, C, or D)")
    soil_description: str
    initial_abstraction_ratio_lambda: float = Field(..., ge=0.01, le=0.5)
    available_lambda_options: List[float]
    curve_numbers: Dict[str, CurveNumberItem]
    manning_roughness: Dict[str, float]
    rational_coefficients: Dict[str, float]
    depression_storage_mm: Dict[str, float]
    risk_score_weights: Dict[str, float]

class HydrologyConfigUpdate(BaseModel):
    soil_hydrologic_group: Optional[str] = None
    initial_abstraction_ratio_lambda: Optional[float] = None
    curve_numbers: Optional[Dict[str, CurveNumberItem]] = None
    risk_score_weights: Optional[Dict[str, float]] = None
