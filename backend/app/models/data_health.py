from sqlalchemy import Column, String, Float, DateTime, Integer, Text, Boolean
from datetime import datetime, timezone
from backend.app.database import Base

class ProviderHealthLog(Base):
    __tablename__ = "provider_health_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    provider_name = Column(String(50), nullable=False, index=True)  # Open-Meteo, Copernicus DEM, OSM, NASA GPM, IMD
    provider_type = Column(String(50), nullable=False)  # WEATHER_API, DEM, GIS, SATELLITE
    status = Column(String(20), nullable=False)  # ONLINE, DEGRADED, OFFLINE
    latency_ms = Column(Float, nullable=True)
    last_successful_fetch_utc = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    data_provenance = Column(String(30), nullable=False)  # LIVE, HISTORICAL, SIMULATED
    checked_at_utc = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
