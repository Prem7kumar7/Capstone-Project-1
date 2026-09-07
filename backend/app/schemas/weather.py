from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class CurrentWeatherResponse(BaseModel):
    study_area_id: str
    timestamp_utc: str
    timestamp_ist: str
    temperature_c: Optional[float] = None
    relative_humidity_pct: Optional[float] = None
    precipitation_mm_h: float
    rain_mm: Optional[float] = None
    wind_speed_kmh: Optional[float] = None
    weather_code: Optional[int] = None
    weather_condition: str
    data_source: str
    provenance: str = "LIVE"
    status: str

class HourlyForecastItem(BaseModel):
    timestamp_utc: str
    timestamp_ist: str
    precipitation_mm: float
    precipitation_probability_pct: Optional[float] = None
    temperature_c: Optional[float] = None
    weather_code: Optional[int] = None

class WeatherForecastResponse(BaseModel):
    study_area_id: str
    issued_at_utc: str
    issued_at_ist: str
    forecast_horizon_hours: int = 6
    cumulative_forecast_6h_mm: float
    max_forecast_intensity_mm_h: float
    hourly: List[HourlyForecastItem]
    data_source: str
    provenance: str = "FORECAST"
    model_name: str
    status: str
