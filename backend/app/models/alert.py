from sqlalchemy import Column, String, Float, DateTime, Integer, Text, Boolean, ForeignKey
from datetime import datetime, timezone
from backend.app.database import Base

class AlertAdvisory(Base):
    __tablename__ = "alert_advisories"

    id = Column(String(50), primary_key=True, index=True)
    study_area_id = Column(String(50), ForeignKey("study_areas.id"), nullable=False, index=True)
    run_id = Column(String(50), ForeignKey("flood_prediction_runs.id"), nullable=True, index=True)
    alert_level = Column(String(20), nullable=False)  # GREEN, YELLOW, ORANGE, RED
    headline = Column(String(200), nullable=False)
    location_name = Column(String(150), nullable=False)
    forecast_rainfall_summary = Column(String(100), nullable=False)
    flood_risk_score = Column(Float, nullable=False)
    estimated_depth_bracket = Column(String(50), nullable=False)
    estimated_time_to_impact = Column(String(50), nullable=False)
    recommended_actions = Column(Text, nullable=False)
    data_source = Column(String(100), nullable=False)
    provenance = Column(String(30), nullable=False)  # LIVE, SIMULATED
    is_active = Column(Boolean, default=True)
    issued_at_utc = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    expires_at_utc = Column(DateTime(timezone=True), nullable=True)

class AlertThreshold(Base):
    __tablename__ = "alert_thresholds"

    id = Column(String(50), primary_key=True)
    level = Column(String(20), nullable=False)  # GREEN, YELLOW, ORANGE, RED
    min_rainfall_intensity_mm_h = Column(Float, nullable=False)
    min_cumulative_rainfall_mm = Column(Float, nullable=False)
    min_flood_risk_score = Column(Float, nullable=False)
    description = Column(String(255), nullable=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
