from fastapi import APIRouter
from backend.app.schemas.hydrology_config import HydrologyConfigSchema, HydrologyConfigUpdate
from backend.app.hydrology.config_loader import hydrology_config_manager

router = APIRouter(prefix="/hydrology", tags=["Hydrology Configuration"])

@router.get("/config")
def get_hydrology_config():
    """Returns data-driven SCS-CN parameters, soil groups, and hydraulic coefficients."""
    return hydrology_config_manager.get_config()

@router.put("/config")
def update_hydrology_config(updates: HydrologyConfigUpdate):
    """Allows administrators to calibrate curve numbers or abstraction ratio lambda."""
    clean_updates = {k: v for k, v in updates.model_dump().items() if v is not None}
    updated = hydrology_config_manager.update_config(clean_updates)
    return {
        "status": "SUCCESS",
        "message": "Hydrology parameters updated and persisted.",
        "config": updated
    }
