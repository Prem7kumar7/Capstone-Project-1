# Data Sources, Transparency & Provenance Catalog

In accordance with scientific integrity guidelines, every data layer within this system has documented provenance, licensing, and update frequencies.

---

## 1. Weather & Precipitation Data

### A. Open-Meteo Global NWP Forecast API
- **Source**: Open-Meteo GmbH
- **Models**: ECMWF IFS (9 km), GFS (13 km), DWD ICON (7 km) multi-model blend
- **Parameters**: 15-minute and hourly precipitation (mm), temperature, relative humidity, wind speed, weather codes
- **Provenance**: `LIVE` (real-time observation) & `FORECAST` (0–6 hour horizon)
- **Licensing**: Open Data Commons Open Database License (ODbL) / Attribution-NonCommercial
- **Fallback Strategy**: In-memory cache TTL (15 min); if unreachable, reports `DATA UNAVAILABLE — awaiting source update` without generating fake numbers.

### B. NASA GPM IMERG (Integrated Multi-satellitE Retrievals for GPM)
- **Source**: NASA Earth Science Data and Information System (ESDIS)
- **Resolution**: 0.1° x 0.1° (~10 km), 30-minute latency for Early Run
- **Provenance**: `SATELLITE_PRECIPITATION`
- **Adapter State**: DORMANT interface. Requires NASA Earthdata authentication token.

### C. India Meteorological Department (IMD)
- **Source**: IMD Regional Meteorological Centre, Chandigarh / New Delhi
- **Coverage**: District Kapurthala / Jalandhar
- **Provenance**: `HISTORICAL` / `GOVERNMENT_OFFICIAL`
- **Adapter State**: DORMANT interface awaiting official API gateway credential activation.

---

## 2. Elevation & Topographic Data

### Copernicus DEM GLO-30 / SRTM 90m
- **Source**: European Space Agency (ESA) Copernicus Programme / NASA SRTM
- **Vertical Accuracy**: < 4 meters
- **Spatial Resolution**: 30 meters
- **Provenance**: `HISTORICAL_SATELLITE`
- **Application**: Ground surface elevation, topographic slope ($\theta$), flow direction, Topographic Wetness Index (TWI), and relative depression storage.

---

## 3. Geospatial Vector Data

### A. Lovely Professional University (LPU) Campus Boundary
- **Source**: OpenStreetMap Nominatim
- **OSM Identifier**: Way `422435593`
- **Coordinates**: Bounding Box `[31.2457534, 31.2609695, 75.6978055, 75.7092374]`
- **Provenance**: `HISTORICAL` (Verified)
- **Licensing**: OpenStreetMap Foundation (ODbL 1.0)

### B. National Highway 44 (NH-44 / Grand Trunk Road)
- **Source**: OpenStreetMap Highway Trunk Network
- **Segment**: Jalandhar – Phagwara corridor passing LPU Main Gate and Chaheru Bridge
- **Provenance**: `HISTORICAL` (Verified)

---

## 4. Drainage Network Status

- **Sub-Surface Storm Sewers & Inverts**: **NOT AVAILABLE / UNVERIFIED**
- **Policy**: No fictitious pipe dimensions or invert elevations are invented. The platform explicitly reports drainage data as unavailable and executes the **Terrain + Land-Cover Runoff Susceptibility Model**.
- **Hydraulic Engine**: The EPA SWMM coupler is kept in a `DORMANT` state until an official university/municipal `.inp` survey model is provided.

---

## 5. Summary Matrix of Data Provenance Labels

| Layer / Feature | Active Source | Provenance Label | Update Frequency | Integrity Rule |
| :--- | :--- | :--- | :--- | :--- |
| **Current Weather** | Open-Meteo API | `LIVE` | 15 Minutes | No invented rain values |
| **0–6h Forecast** | Open-Meteo NWP | `FORECAST` | Hourly | Explicitly marked as forecast |
| **Campus Boundary** | OSM Way 422435593 | `HISTORICAL` | Static | Only verified geometries |
| **Road Network** | OSM Trunk NH-44 | `HISTORICAL` | Static | Only verified geometries |
| **Drainage Network** | Field Survey (Pending) | `UNVERIFIED` | N/A | Flagged NOT AVAILABLE |
| **Flood Risk Score** | Hydrological Engine | `DERIVED` | Dynamic | Uncalibrated 0–100 index |
| **Water Depth Bracket**| SCS Runoff Model | `DERIVED` | Dynamic | Tagged `[MODEL ESTIMATE]` |
| **Time-to-Flood** | Conveyance Model | `DERIVED` | Dynamic | Tagged `[ESTIMATED]` |
| **Simulation Mode** | Synthetic Generator | `SIMULATED` | Interactive | Unmissable warning banner |
| **Accuracy Metrics** | Field Log Database | `VALIDATED` | On-Demand | Reports Insufficient if empty |
