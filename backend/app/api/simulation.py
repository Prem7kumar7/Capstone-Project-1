from fastapi import APIRouter
from backend.app.schemas.simulation import SimulationScenarioRequest, SimulationRunResponse
from backend.app.risk.pipeline_service import execute_nowcasting_pipeline

router = APIRouter(prefix="/simulation", tags=["Simulation Mode"])

@router.post("/run", response_model=SimulationRunResponse)
async def run_simulation_scenario(scenario: SimulationScenarioRequest):
    """
    Executes a controlled simulation scenario for what-if stress testing.
    Feeds synthetic parameters into the exact same hydrological and flood-risk pipeline.
    Output is strictly tagged as SIMULATED with a prominent disclaimer banner.
    """
    results = await execute_nowcasting_pipeline(
        is_simulation=True,
        sim_intensity_mm_h=scenario.rainfall_intensity_mm_h,
        sim_cumulative_mm=scenario.cumulative_rainfall_mm,
        sim_clogging_fraction=scenario.drainage_clogging_pct / 100.0
    )

    return {
        "simulation_banner": "SIMULATION MODE — values are synthetic and are NOT real observations.",
        "is_simulation": True,
        "scenario": scenario,
        "results": results
    }
