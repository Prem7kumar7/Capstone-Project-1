"""
Queries Copernicus DEM GLO-30 / Open-Meteo Elevation API for study area coordinates.
"""
import json
import urllib.request
from pathlib import Path

REGIONS = [
    {"id": "lpu_main_campus", "name": "LPU Campus", "lat": 31.2533, "lon": 75.7033},
    {"id": "chaheru", "name": "Chaheru Corridor", "lat": 31.2590, "lon": 75.6940},
    {"id": "phagwara_urban", "name": "Phagwara Urban Basin", "lat": 31.2207, "lon": 75.7725},
    {"id": "jalandhar_metro", "name": "Jalandhar Urban Metro", "lat": 31.3260, "lon": 75.5762}
]

lats = ",".join(str(r["lat"]) for r in REGIONS)
lons = ",".join(str(r["lon"]) for r in REGIONS)
url = f"https://api.open-meteo.com/v1/elevation?latitude={lats}&longitude={lons}"

req = urllib.request.Request(url, headers={"User-Agent": "LPU-Flood-Nowcast/1.0"})
with urllib.request.urlopen(req, timeout=10) as resp:
    data = json.loads(resp.read().decode())
    elevations = data.get("elevation", [])
    for r, el in zip(REGIONS, elevations):
        print(f"Region: {r['name']} ({r['lat']}, {r['lon']}) -> Elevation: {el} m MSL (Copernicus DEM 30m)")
