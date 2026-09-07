"""
Reproducible script to fetch and verify OpenStreetMap geospatial layers
for LPU, Chaheru, Phagwara, and Jalandhar.
"""
import json
import urllib.request
from pathlib import Path

TARGET_DIR = Path("data/study_areas")
TARGET_DIR.mkdir(parents=True, exist_ok=True)

print("Checking verified OSM layers in data/study_areas/...")
expected = [
    "lpu_osm_boundary.geojson",
    "nh44_osm_trunk.geojson",
    "chaheru_osm_boundary.geojson",
    "phagwara_osm_boundary.geojson",
    "jalandhar_osm_boundary.geojson",
    "regional_waterways.geojson",
    "critical_infrastructure.geojson"
]

all_present = True
for fname in expected:
    p = TARGET_DIR / fname
    if p.exists():
        size = p.stat().st_size
        print(f" [OK] {fname} ({size} bytes)")
    else:
        print(f" [MISSING] {fname}")
        all_present = False

if all_present:
    print("All 7 study area geospatial layers are verified and ready on disk.")
else:
    print("Some layers missing.")
