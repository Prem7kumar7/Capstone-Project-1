from fastapi import APIRouter
from backend.app.providers.open_meteo import open_meteo_provider

router = APIRouter(prefix="/weather", tags=["Weather & Rainfall"])

@router.get("/current")
async def get_current_weather():
    """Returns real-time weather observations from Open-Meteo with data provenance and quality metadata."""
    data = await open_meteo_provider.get_current_and_forecast()
    return {
        "study_area_id": data["study_area_id"],
        "timestamp_utc": data["timestamp_utc"],
        "timestamp_ist": data["timestamp_ist"],
        "temperature_c": data["temperature_c"],
        "relative_humidity_pct": data["relative_humidity_pct"],
        "precipitation_mm_h": data["precipitation_mm_h"],
        "rain_mm": data["rain_mm"],
        "wind_speed_kmh": data["wind_speed_kmh"],
        "weather_code": data["weather_code"],
        "weather_condition": data["weather_condition"],
        "data_source": data["data_source"],
        "provenance": data["provenance"],
        "status": data["status"]
    }

@router.get("/forecast")
async def get_forecast():
    """Returns 0-6 hour rainfall forecast from Open-Meteo NWP model with hourly breakdown."""
    data = await open_meteo_provider.get_current_and_forecast()
    return {
        "study_area_id": data["study_area_id"],
        "issued_at_utc": data["timestamp_utc"],
        "issued_at_ist": data["timestamp_ist"],
        "forecast_horizon_hours": data["forecast_horizon_hours"],
        "cumulative_forecast_6h_mm": data["cumulative_forecast_6h_mm"],
        "max_forecast_intensity_mm_h": data["max_forecast_intensity_mm_h"],
        "hourly": data["hourly_forecast"],
        "data_source": data["data_source"],
        "provenance": "FORECAST",
        "model_name": "Open-Meteo NWP ECMWF/GFS Blend",
        "status": data["status"]
    }
