import math
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime, timezone
import zoneinfo

IST = zoneinfo.ZoneInfo("Asia/Kolkata")

def utc_to_ist_str(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    ist_dt = dt.astimezone(IST)
    return ist_dt.strftime("%Y-%m-%d %I:%M:%S %p IST")

def haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000.0  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def load_geojson_safe(file_path: Path) -> Dict[str, Any]:
    if not file_path.exists():
        return {"type": "FeatureCollection", "features": [], "metadata": {"status": "file_not_found"}}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"type": "FeatureCollection", "features": [], "metadata": {"error": str(e)}}
