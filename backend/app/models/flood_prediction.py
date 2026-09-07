from sqlalchemy import Column, String, Float, DateTime, Integer, Text, Boolean, ForeignKey
from datetime import datetime, timezone
from backend.app.database import Base

class FloodPredictionRun(Base):
    __tablename__ = "flood_prediction_runs"

    id = Column(String(50), primary_key=True, index=True)  # UF-YYYYMMDD-UUID
    study_area_id = Column(String(50), ForeignKey("study_areas.id"), nullable=False, index=True)
    run_timestamp_utc = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    execution_mode = Column(String(20), nullable=False)  # LIVE, SIMULATED
    modelling_mode = Column(String(50), nullable=False)  # TERRAIN_RUNOFF_SUSCEPTIBILITY, SIMPLIFIED_RUNOFF_LIMITATION, SWMM_HYDRAULIC
    
    # Input Hydrology Summary
    current_rainfall_mm_h = Column(Float, default=0.0)
    forecast_cumulative_6h_mm = Column(Float, default=0.0)
    max_forecast_intensity_mm_h = Column(Float, default=0.0)
    drainage_clogging_fraction = Column(Float, default=0.0)  # Used in simulation
    
    # Risk Results
    max_flood_risk_score = Column(Float, nullable=False)  # 0 to 100
    overall_severity = Column(String(20), nullable=False)  # VERY_LOW, LOW, MODERATE, HIGH, EXTREME
    highest_estimated_depth_bracket = Column(String(30), nullable=False)  # < 0.10 m, 0.10-0.30 m, etc.
    earliest_time_to_flood = Column(String(30), nullable=True)  # 0-30 min, 30-60 min, etc.
    affected_hotspots_count = Column(Integer, default=0)
    
    # Provenance & Confidence
    confidence_level = Column(String(20), default="MEDIUM")  # HIGH, MEDIUM, LOW
    data_sources = Column(Text, nullable=True)  # JSON or comma-separated
    model_version = Column(String(30), default="0.1.0-alpha")
    is_simulation = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class FloodHotspot(Base):
    __tablename__ = "flood_hotspots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(50), ForeignKey("flood_prediction_runs.id"), nullable=False, index=True)
    location_name = Column(String(150), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    elevation_m = Column(Float, nullable=True)
    
    # Hydrology & Risk Metrics
    runoff_volume_m3 = Column(Float, nullable=True)
    flood_risk_score = Column(Float, nullable=False)  # 0 to 100
    risk_category = Column(String(20), nullable=False)  # VERY_LOW, LOW, MODERATE, HIGH, EXTREME
    estimated_depth_bracket = Column(String(30), nullable=False)  # MODEL ESTIMATE
    estimated_depth_m = Column(Float, nullable=True)
    estimated_time_to_flood = Column(String(30), nullable=False)  # ESTIMATED
    
    # Context
    susceptibility_factors = Column(Text, nullable=True)  # JSON describing topography/drainage
    data_provenance = Column(String(30), nullable=False)  # DERIVED, SIMULATED
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
