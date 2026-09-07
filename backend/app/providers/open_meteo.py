import time
import httpx
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from backend.app.config import settings
from backend.app.providers.base import BaseProvider
from backend.app.utils.geo import utc_to_ist_str
from backend.app.utils.logging import logger

class OpenMeteoProvider(BaseProvider):
    def __init__(self):
        super().__init__(provider_name="Open-Meteo NWP", provider_type="WEATHER_API")
        self._cache: Dict[str, Any] = {}
        self._cache_timestamp: float = 0.0

    async def check_health(self) -> Dict[str, Any]:
        start = time.time()
        try:
            async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT_SECONDS) as client:
                params = {
                    "latitude": settings.DEFAULT_LAT,
                    "longitude": settings.DEFAULT_LON,
                    "current": "temperature_2m",
                    "forecast_days": 1
                }
                r = await client.get(settings.OPEN_METEO_FORECAST_URL, params=params)
                latency = round((time.time() - start) * 1000, 1)
                if r.status_code == 200:
                    self.last_status = "ONLINE"
                    self.last_latency_ms = latency
                    self.last_fetch_utc = datetime.now(timezone.utc)
                    self.last_error = None
                    return {"status": "ONLINE", "latency_ms": latency, "provider": self.provider_name}
                else:
                    self.last_status = "DEGRADED"
                    self.last_latency_ms = latency
                    self.last_error = f"HTTP {r.status_code}"
                    return {"status": "DEGRADED", "latency_ms": latency, "error": self.last_error}
        except Exception as e:
            latency = round((time.time() - start) * 1000, 1)
            self.last_status = "OFFLINE"
            self.last_latency_ms = latency
            self.last_error = str(e)
            return {"status": "OFFLINE", "latency_ms": latency, "error": str(e)}

    async def get_current_and_forecast(self, lat: float = None, lon: float = None) -> Dict[str, Any]:
        lat = lat or settings.DEFAULT_LAT
        lon = lon or settings.DEFAULT_LON
        now = time.time()

        # In-memory cache check
        if self._cache and (now - self._cache_timestamp) < settings.CACHE_TTL_SECONDS:
            logger.info("Serving Open-Meteo weather data from in-memory cache.")
            return self._cache

        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,precipitation,rain,weather_code,wind_speed_10m",
            "hourly": "precipitation,rain,precipitation_probability,temperature_2m,weather_code",
            "forecast_days": 2,
            "timezone": "Asia/Kolkata"
        }

        start = time.time()
        try:
            async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT_SECONDS) as client:
                r = await client.get(settings.OPEN_METEO_FORECAST_URL, params=params)
                latency = round((time.time() - start) * 1000, 1)
                
                if r.status_code != 200:
                    self.last_status = "DEGRADED"
                    self.last_latency_ms = latency
                    self.last_error = f"HTTP {r.status_code}"
                    raise RuntimeError(f"Open-Meteo returned HTTP {r.status_code}")

                data = r.json()
                self.last_status = "ONLINE"
                self.last_latency_ms = latency
                self.last_fetch_utc = datetime.now(timezone.utc)
                self.last_error = None

                # Process current observation
                curr = data.get("current", {})
                hourly = data.get("hourly", {})

                # Extract next 6 hours forecast
                hourly_times = hourly.get("time", [])
                hourly_precip = hourly.get("precipitation", [])
                hourly_prob = hourly.get("precipitation_probability", [])
                hourly_temp = hourly.get("temperature_2m", [])
                hourly_codes = hourly.get("weather_code", [])

                # Map weather code to human description
                w_code = curr.get("weather_code", 0)
                condition = self._map_weather_code(w_code)

                # Assemble 0-6h items
                forecast_items = []
                cum_6h = 0.0
                max_int = 0.0
                
                # Take up to 6 hourly steps from now
                for i in range(min(6, len(hourly_times))):
                    p = float(hourly_precip[i]) if i < len(hourly_precip) else 0.0
                    cum_6h += p
                    if p > max_int:
                        max_int = p
                    forecast_items.append({
                        "timestamp_utc": hourly_times[i],
                        "timestamp_ist": hourly_times[i] + " IST",
                        "precipitation_mm": round(p, 1),
                        "precipitation_probability_pct": float(hourly_prob[i]) if i < len(hourly_prob) and hourly_prob[i] is not None else 0.0,
                        "temperature_c": float(hourly_temp[i]) if i < len(hourly_temp) else None,
                        "weather_code": int(hourly_codes[i]) if i < len(hourly_codes) else None
                    })

                now_utc = datetime.now(timezone.utc)
                processed = {
                    "study_area_id": settings.DEFAULT_STUDY_AREA_ID,
                    "timestamp_utc": now_utc.isoformat(),
                    "timestamp_ist": utc_to_ist_str(now_utc),
                    "temperature_c": curr.get("temperature_2m"),
                    "relative_humidity_pct": curr.get("relative_humidity_2m"),
                    "precipitation_mm_h": float(curr.get("precipitation", 0.0)),
                    "rain_mm": float(curr.get("rain", 0.0)),
                    "wind_speed_kmh": curr.get("wind_speed_10m"),
                    "weather_code": w_code,
                    "weather_condition": condition,
                    "data_source": "Open-Meteo Global NWP Model (ECMWF/GFS blend)",
                    "provenance": "LIVE",
                    "status": "LIVE_DATA_CONNECTED",
                    "forecast_horizon_hours": 6,
                    "cumulative_forecast_6h_mm": round(cum_6h, 1),
                    "max_forecast_intensity_mm_h": round(max_int, 1),
                    "hourly_forecast": forecast_items
                }

                # Update cache
                self._cache = processed
                self._cache_timestamp = now
                return processed

        except Exception as e:
            logger.error(f"Failed to retrieve weather from Open-Meteo: {e}")
            self.last_status = "OFFLINE"
            self.last_error = str(e)
            
            # If cache exists, return it with warning
            if self._cache:
                self._cache["status"] = "SERVED_FROM_STALE_CACHE"
                return self._cache

            # Return graceful unavailable response
            now_utc = datetime.now(timezone.utc)
            return {
                "study_area_id": settings.DEFAULT_STUDY_AREA_ID,
                "timestamp_utc": now_utc.isoformat(),
                "timestamp_ist": utc_to_ist_str(now_utc),
                "temperature_c": None,
                "relative_humidity_pct": None,
                "precipitation_mm_h": 0.0,
                "rain_mm": 0.0,
                "wind_speed_kmh": None,
                "weather_code": None,
                "weather_condition": "DATA UNAVAILABLE — awaiting source update",
                "data_source": "Open-Meteo (Connection Pending)",
                "provenance": "LIVE",
                "status": "LIVE_DATA_TEMPORARILY_UNAVAILABLE",
                "forecast_horizon_hours": 6,
                "cumulative_forecast_6h_mm": 0.0,
                "max_forecast_intensity_mm_h": 0.0,
                "hourly_forecast": []
            }

    def _map_weather_code(self, code: int) -> str:
        codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        return codes.get(code, "Unknown")

open_meteo_provider = OpenMeteoProvider()
