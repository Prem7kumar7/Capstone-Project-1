from typing import Dict, Any
from backend.app.providers.base import BaseProvider

class GPMProvider(BaseProvider):
    """Adapter interface for NASA GPM IMERG Early/Late precipitation product."""
    def __init__(self):
        super().__init__(provider_name="NASA GPM IMERG", provider_type="SATELLITE_PRECIPITATION")

    async def check_health(self) -> Dict[str, Any]:
        return {
            "provider": self.provider_name,
            "status": "DORMANT",
            "is_active": False,
            "latency_ms": None,
            "notes": "NASA Earthdata bearer token required for live HDF5/GeoTIFF raster streaming. Currently using Open-Meteo NWP precipitation feeds."
        }

class IMDProvider(BaseProvider):
    """Adapter interface for India Meteorological Department (IMD) open weather services."""
    def __init__(self):
        super().__init__(provider_name="IMD (India Meteorological Department)", provider_type="NATIONAL_WEATHER_AGENCY")

    async def check_health(self) -> Dict[str, Any]:
        return {
            "provider": self.provider_name,
            "status": "DORMANT",
            "is_active": False,
            "latency_ms": None,
            "notes": "IMD public API adapter interface configured for District Kapurthala / Jalandhar. Awaiting official API gateway activation."
        }

gpm_provider = GPMProvider()
imd_provider = IMDProvider()
