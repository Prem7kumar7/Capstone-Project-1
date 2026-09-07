from sqlalchemy import Column, String, Float, DateTime, Text, Boolean, Integer
from datetime import datetime, timezone
from backend.app.database import Base

class StudyArea(Base):
    __tablename__ = "study_areas"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    city = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    country = Column(String(50), default="India")
    centroid_lat = Column(Float, nullable=False)
    centroid_lon = Column(Float, nullable=False)
    radius_km = Column(Float, default=3.5)
    boundary_geojson = Column(Text, nullable=True)
    drainage_mode = Column(String(50), default="SIMPLIFIED_RUNOFF_LIMITATION")  # HYDRAULIC_SWMM, SIMPLIFIED_RUNOFF_LIMITATION, TERRAIN_SUSCEPTIBILITY
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
