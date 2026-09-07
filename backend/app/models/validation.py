from sqlalchemy import Column, String, Float, DateTime, Integer, Text, Boolean
from datetime import datetime, timezone
from backend.app.database import Base

class HistoricalValidationEvent(Base):
    __tablename__ = "validation_events"

    id = Column(String(50), primary_key=True, index=True)
    study_area_id = Column(String(50), nullable=False, index=True)
    event_timestamp_utc = Column(DateTime(timezone=True), nullable=False, index=True)
    location_name = Column(String(150), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Rainfall Input
    observed_rainfall_24h_mm = Column(Float, nullable=False)
    peak_intensity_mm_h = Column(Float, nullable=True)
    lead_time_hours = Column(Float, nullable=False)
    
    # Model Predictions
    predicted_risk_score = Column(Float, nullable=False)
    predicted_risk_category = Column(String(30), nullable=False)
    predicted_depth_bracket = Column(String(30), nullable=False)
    predicted_depth_m = Column(Float, nullable=True)
    
    # Ground-Truth Observations (MUST be genuine field observations)
    observed_flooded = Column(Boolean, nullable=False)
    observed_depth_m = Column(Float, nullable=True)
    observed_depth_bracket = Column(String(30), nullable=True)
    
    # Evidence & Provenance
    ground_truth_source = Column(String(200), nullable=False)  # e.g., "DDMA Kapurthala official report", "Campus CCTV water gauge"
    notes = Column(Text, nullable=True)
    verified_by = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
