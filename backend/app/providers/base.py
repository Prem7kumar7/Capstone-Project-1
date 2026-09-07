from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime, timezone

class BaseProvider(ABC):
    """Abstract base class for all external data providers."""
    def __init__(self, provider_name: str, provider_type: str):
        self.provider_name = provider_name
        self.provider_type = provider_type
        self.last_status = "UNKNOWN"
        self.last_latency_ms = 0.0
        self.last_fetch_utc = None
        self.last_error = None

    @abstractmethod
    async def check_health(self) -> Dict[str, Any]:
        """Verify API connectivity, rate limits, and latency."""
        pass
