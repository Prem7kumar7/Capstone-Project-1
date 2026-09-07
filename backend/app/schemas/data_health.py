from typing import List, Optional, Dict
from pydantic import BaseModel

class ProviderStatusItem(BaseModel):
    provider_name: str
    provider_type: str
    status: str  # ONLINE, DEGRADED, OFFLINE
    latency_ms: Optional[float] = None
    last_updated_ist: str
    data_provenance: str
    notes: Optional[str] = None

class SystemHealthResponse(BaseModel):
    system_status: str  # OPERATIONAL, DEGRADED, OFFLINE
    overall_mode: str   # LIVE, SIMULATION
    active_study_area: str
    checked_at_ist: str
    providers: List[ProviderStatusItem]
