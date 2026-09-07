import time
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from backend.app.config import settings
from backend.app.providers.base import BaseProvider
from backend.app.utils.logging import logger

class OpenMeteoElevationProvider(BaseProvider):
    """Provides digital elevation model (DEM) data via Open-Meteo Elevation API (Copernicus 30m / SRTM 90m)."""
    def __init__(self):
        super().__init__(provider_name="Copernicus DEM (Open-Meteo)", provider_type="DEM")
        self._elevation_cache: Dict[str, float] = {}

    async def check_health(self) -> Dict[str, Any]:
        start = time.time()
        try:
            async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT_SECONDS) as client:
                params = {"latitude": settings.DEFAULT_LAT, "longitude": settings.DEFAULT_LON}
                r = await client.get(settings.OPEN_METEO_ELEVATION_URL, params=params)
                latency = round((time.time() - start) * 1000, 1)
                if r.status_code == 200:
                    self.last_status = "ONLINE"
                    self.last_latency_ms = latency
                    self.last_fetch_utc = datetime.now(timezone.utc)
                    return {"status": "ONLINE", "latency_ms": latency, "provider": self.provider_name}
                else:
                    self.last_status = "DEGRADED"
                    self.last_latency_ms = latency
                    return {"status": "DEGRADED", "latency_ms": latency}
        except Exception as e:
            latency = round((time.time() - start) * 1000, 1)
            self.last_status = "OFFLINE"
            self.last_latency_ms = latency
            self.last_error = str(e)
            return {"status": "OFFLINE", "latency_ms": latency, "error": str(e)}

    async def get_elevation_points(self, coords: List[tuple]) -> List[float]:
        """Fetch elevation for a list of (lat, lon) coordinates."""
        if not coords:
            return []

        # Check cache
        uncached_indices = []
        elevations = [None] * len(coords)

        for i, (lat, lon) in enumerate(coords):
            k = f"{lat:.4f},{lon:.4f}"
            if k in self._elevation_cache:
                elevations[i] = self._elevation_cache[k]
            else:
                uncached_indices.append(i)

        if not uncached_indices:
            return elevations

        lats = ",".join([f"{coords[i][0]:.5f}" for i in uncached_indices])
        lons = ",".join([f"{coords[i][1]:.5f}" for i in uncached_indices])

        try:
            async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT_SECONDS) as client:
                r = await client.get(settings.OPEN_METEO_ELEVATION_URL, params={"latitude": lats, "longitude": lons})
                if r.status_code == 200:
                    api_elevations = r.json().get("elevation", [])
                    for idx_pos, orig_idx in enumerate(uncached_indices):
                        elev = float(api_elevations[idx_pos]) if idx_pos < len(api_elevations) else 238.0
                        elevations[orig_idx] = elev
                        k = f"{coords[orig_idx][0]:.4f},{coords[orig_idx][1]:.4f}"
                        self._elevation_cache[k] = elev
                else:
                    for orig_idx in uncached_indices:
                        elevations[orig_idx] = 238.0  # Fallback to Phagwara regional base
        except Exception as e:
            logger.warning(f"Elevation query failed: {e}. Using regional baseline (238m).")
            for orig_idx in uncached_indices:
                elevations[orig_idx] = 238.0

        return elevations

elevation_provider = OpenMeteoElevationProvider()
