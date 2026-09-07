from sqlalchemy import Column, String, Float, DateTime, Integer, Text, ForeignKey
from datetime import datetime, timezone
from backend.app.database import Base

class WeatherObservation(Base):
    __tablename__ = "weather_observations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    study_area_id = Column(String(50), ForeignKey("study_areas.id"), nullable=False, index=True)
    timestamp_utc = Column(DateTime(timezone=True), nullable=False, index=True)
    temperature_c = Column(Float, nullable=True)
    relative_humidity_pct = Column(Float, nullable=True)
    precipitation_mm_h = Column(Float, nullable=False, default=0.0)
    rain_mm = Column(Float, nullable=True, default=0.0)
    wind_speed_kmh = Column(Float, nullable=True)
    weather_code = Column(Integer, nullable=True)
    data_source = Column(String(100), nullable=False)
    provenance = Column(String(30), nullable=False)  # LIVE, HISTORICAL, SIMULATED
    raw_payload = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class RainfallForecast(Base):
    __tablename__ = "rainfall_forecasts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    study_area_id = Column(String(50), ForeignKey("study_areas.id"), nullable=False, index=True)
    issued_at_utc = Column(DateTime(timezone=True), nullable=False, index=True)
    forecast_time_utc = Column(DateTime(timezone=True), nullable=False, index=True)
    horizon_hours = Column(Float, nullable=False)
    expected_precipitation_mm = Column(Float, nullable=False)
    precipitation_probability_pct = Column(Float, nullable=True)
    data_source = Column(String(100), nullable=False)
    provenance = Column(String(30), nullable=False)  # FORECAST, SIMULATED
    model_name = Column(String(100), default="Open-Meteo-NWP")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
