from fastapi import APIRouter
from backend.app.api.study_area import router as study_area_router
from backend.app.api.weather import router as weather_router
from backend.app.api.nowcasting import router as nowcasting_router
from backend.app.api.flood import router as flood_router
from backend.app.api.simulation import router as simulation_router
from backend.app.api.alerts import router as alerts_router
from backend.app.api.data_health import router as data_health_router
from backend.app.api.validation import router as validation_router
from backend.app.api.hydrology_config import router as hydrology_config_router

api_router = APIRouter()

api_router.include_router(study_area_router)
api_router.include_router(weather_router)
api_router.include_router(nowcasting_router)
api_router.include_router(flood_router)
api_router.include_router(simulation_router)
api_router.include_router(alerts_router)
api_router.include_router(data_health_router)
api_router.include_router(validation_router)
api_router.include_router(hydrology_config_router)
