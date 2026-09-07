from pydantic import BaseModel, Field
from backend.app.schemas.flood import FloodPredictionRunResponse

class SimulationScenarioRequest(BaseModel):
    study_area_id: str = "lpu_main_campus"
    rainfall_intensity_mm_h: float = Field(..., ge=0.0, le=200.0, description="Synthetic constant rainfall intensity (mm/h)")
    cumulative_rainfall_mm: float = Field(..., ge=0.0, le=500.0, description="Synthetic total storm accumulation (mm)")
    storm_duration_hours: float = Field(default=3.0, ge=0.5, le=12.0, description="Storm duration (hours)")
    drainage_clogging_pct: float = Field(default=0.0, ge=0.0, le=100.0, description="Percentage of drainage conveyance blocked (0-100%)")
    scenario_label: str = Field(default="Custom Simulation Scenario")

class SimulationRunResponse(BaseModel):
    simulation_banner: str = "SIMULATION MODE — values are synthetic and are NOT real observations."
    is_simulation: bool = True
    scenario: SimulationScenarioRequest
    results: FloodPredictionRunResponse
