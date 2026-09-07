# Comprehensive Geospatial & Hydrological Data Catalog

## SIH26085 – Urban Flood Nowcasting System
**Study Region**: Lovely Professional University (LPU), Chaheru/Chiheru, Phagwara, and Jalandhar (Punjab, India).

In accordance with the **Strict 8-Step Data-Verification Protocol**, every dataset has been verified, downloaded or accessed directly, schema-inspected, and cataloged.

| Dataset Name | Source Organization | Official URL | Download / API URL | Spatial Coverage | Temporal Coverage | Spatial Resolution | Temporal Resolution | Format | License | Status | Confidence | Provenance |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Open-Meteo Global NWP & Real-Time Weather** | Open-Meteo GmbH (ECMWF, DWD, GFS blend) | [open-meteo.com](https://open-meteo.com) | `https://api.open-meteo.com/v1/forecast` | Global (LPU, Chaheru, Phagwara, Jalandhar) | Real-time + 7-day hourly forecast | 7 - 11 km grid | 15-minute / Hourly | JSON REST API | ODbL / CC-BY 4.0 | **AVAILABLE** | HIGH | `LIVE` / `FORECAST` |
| **Copernicus DEM GLO-30 / SRTM** | European Space Agency (ESA) / NASA | [spacedata.copernicus.eu](https://spacedata.copernicus.eu) | `https://api.open-meteo.com/v1/elevation` | Punjab (31.18°N–31.36°N, 75.52°E–75.81°E) | Static Topographic Baseline | 30 meters | Static | GeoTIFF / REST API | Public Domain / Open Access | **AVAILABLE** | VERY_HIGH | `HISTORICAL_SATELLITE` |
| **OSM Administrative & Campus Boundaries** | OpenStreetMap Contributors | [openstreetmap.org](https://www.openstreetmap.org) | Overpass API / Nominatim | LPU Campus, Chaheru, Phagwara, Jalandhar | Current georeferenced extents | Vector Polygon (< 5m fidelity) | Continuously updated | GeoJSON | ODbL 1.0 | **AVAILABLE** | VERY_HIGH | `HISTORICAL_VERIFIED` |
| **OSM Road Network & NH-44 Corridor** | OpenStreetMap Contributors / NHAI | [openstreetmap.org](https://www.openstreetmap.org) | Overpass API | NH-44 Grand Trunk Road & urban networks | Current | Vector Polyline | Static / Continuous | GeoJSON | ODbL 1.0 | **AVAILABLE** | VERY_HIGH | `HISTORICAL_VERIFIED` |
| **Regional Waterways & Natural Drainage Chos** | Punjab Water Resources Department / OSM | [irrigation.punjab.gov.in](https://irrigation.punjab.gov.in) | Overpass API | Kali Bein, Kala Sanghian, Chaheru stream, Phagwara Choe | Current drainage | Vector Polyline | Static | GeoJSON | ODbL 1.0 / Open Govt Data | **AVAILABLE** | HIGH | `DERIVED_MAPPED_CHANNELS` |
| **Critical Civic Infrastructure** | OpenStreetMap / MC Jalandhar / MC Phagwara | [openstreetmap.org](https://www.openstreetmap.org) | Overpass API | LPU Uni-Hospital, Civil Hospitals, Railway Stations, Fire Sub-stations | Current | Vector Point | Static | GeoJSON | ODbL 1.0 | **AVAILABLE** | VERY_HIGH | `HISTORICAL_VERIFIED` |
| **NRSC / Sentinel-1 SAR Punjab Floods Assessment** | ISRO National Remote Sensing Centre (NRSC) / ESA | [bhuvan-app1.nrsc.gov.in](https://bhuvan-app1.nrsc.gov.in) | NRSC DMSP Technical Flood Bulletin | Kapurthala & Jalandhar districts | July 9–15, 2023 disaster event | 10 - 20 meters (SAR backscatter) | Episodic disaster pass | GeoJSON / JSON | Public Disaster Bulletin / Open Access | **AVAILABLE** | HIGH | `HISTORICAL_SATELLITE_OBSERVED` |
| **Sub-surface Pipe Dimensions & Invert Levels** | MC Jalandhar / MC Phagwara / LPU Estate | Not published online | UNAVAILABLE (Private engineering drawings) | LPU, Phagwara, Jalandhar | N/A | N/A | N/A | CAD / Invert DB | Internal / Municipal Property | **UNAVAILABLE** | N/A | `UNAVAILABLE` |

*A machine-readable CSV version is saved at `data/metadata/data_catalog.csv`.*
