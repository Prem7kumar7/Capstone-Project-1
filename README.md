# Urban Flood Nowcasting System: Lovely Professional University (LPU)

> **SIH 2026 Problem Statement**: *“Urban Flood Nowcasting System through Dynamic Coupling of Rainfall Forecasts and Urban Drainage Network Models”*  
> **Primary Study Area**: Lovely Professional University (LPU), Jalandhar–Delhi Grand Trunk Road (NH-44), Phagwara, Kapurthala / Jalandhar, Punjab, India.

---

## 🌊 Overview

The **Urban Flood Nowcasting System** is a production-oriented, modular hydrological nowcasting and disaster management platform. It dynamically couples short-term numerical weather forecasts with digital elevation terrain models, data-driven hydrological runoff equations (SCS-CN and Rational Method), and a decoupled EPA SWMM hydraulic model interface.

Unlike cosmetic mock dashboards, this system is built on **strict scientific transparency**:
- **Zero Fabrication**: Never generates fake sensor readings, fictitious pipe invert levels, or fabricated validation statistics.
- **Data Provenance**: Every metric and layer is explicitly tagged as `LIVE`, `FORECAST`, `HISTORICAL`, `DERIVED`, or `SIMULATED`.
- **Flood Risk Score (0–100)**: Uses an uncalibrated composite engineering risk index rather than falsely claiming statistical probability percentages.
- **Dual Operating Modes**: Features both a **LIVE MONITORING MODE** connected to real-time APIs and a **WHAT-IF SCENARIO SIMULATOR** for stress testing.

---

## 🏗️ Architecture

```
[Open-Meteo Live API]    [Copernicus DEM 30m]    [OSM Verified Vector Base]
         \                        |                        /
          \                       |                       /
           v                      v                      v
    +-------------------------------------------------------------+
    |           Data Ingestion Adapters & Provenance Tagger       |
    +-------------------------------------------------------------+
                                  |
                                  v
    +-------------------------------------------------------------+
    |            0–6h Rainfall Nowcasting Extensible Suite        |
    |      (NWP Blend, Persistence Decay, Trend Extrapolation)    |
    +-------------------------------------------------------------+
                                  |
                                  v
    +-------------------------------------------------------------+
    |             Data-Driven Hydrology & Runoff Engines          |
    |      - Configurable SCS-CN Method (hydrology_params.json)   |
    |      - Rational Peak Runoff (Q = C*I*A)                     |
    |      - Simplified Drainage & Terrain Susceptibility Model   |
    |      - EPA SWMM Coupler (Dormant awaiting .inp network)     |
    +-------------------------------------------------------------+
                                  |
                                  v
    +-------------------------------------------------------------+
    |                 Decision Support & Alerts                   |
    |      - Flood Risk Score (0–100)                             |
    |      - Inundation Depth Bracket [MODEL ESTIMATE]            |
    |      - Estimated Time-to-Flood [ESTIMATED]                  |
    |      - Actionable Advisories (Green, Yellow, Orange, Red)   |
    +-------------------------------------------------------------+
                   |                               |
                   v                               v
    +-----------------------------+ +-----------------------------+
    |  FastAPI Backend (Port 8000)| | Next.js GIS Dashboard (3000)|
    |  PostGIS / SQLite Fallback  | | Leaflet, Recharts, Tailwind |
    +-----------------------------+ +-----------------------------+
```

---

## 🚀 Quick Start Guide

### Option 1: Native Local Run (Zero Configuration Required)

#### 1. Backend (FastAPI):
```bash
# In project root
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```
- Interactive Swagger API Docs: `http://127.0.0.1:8000/docs`
- Health Status: `http://127.0.0.1:8000/health`
- Automatically initializes SQLite database `flood_nowcasting.db`.

#### 2. Frontend (Next.js 14):
```bash
cd frontend
npm run dev
```
- Open your browser at `http://localhost:3000`

---

### Option 2: Docker Compose (Production Deployment)

Runs PostgreSQL 16 + PostGIS 3.4, Redis 7, FastAPI backend, and Next.js frontend in containers:
```bash
docker compose up --build -d
```
- Web Application: `http://localhost:3000`
- REST API: `http://localhost:8000/docs`

---

## 🧪 Automated Testing

The backend includes a comprehensive pytest suite covering hydrology equations, risk scoring, SWMM coupler states, optical flow vectors, and REST endpoints:

```bash
python -m pytest backend/tests -v
```

---

## 📁 Repository Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI entry point
│   │   ├── config.py                   # Pydantic settings
│   │   ├── database.py                 # PostgreSQL / SQLite session
│   │   ├── models/                     # SQLAlchemy models
│   │   ├── schemas/                    # Pydantic v2 schemas
│   │   ├── providers/                  # Open-Meteo, DEM, OSM, GPM, IMD
│   │   ├── nowcasting/                 # NWP, Persistence, Trend models
│   │   ├── advanced_nowcasting/        # 2D Optical Flow advection & ConvLSTM
│   │   ├── hydrology/                  # SCS-CN, Rational, Terrain, SWMM coupler
│   │   ├── risk/                       # Risk scoring, depth brackets, alerts
│   │   └── api/                        # REST endpoint routers
│   └── tests/                          # 25 automated pytest tests
├── config/
│   └── hydrology_params.json           # Data-driven SCS-CN and hydraulic config
├── data/
│   └── study_areas/
│       ├── lpu_osm_boundary.geojson    # Verified OSM polygon (Way 422435593)
│       └── nh44_osm_trunk.geojson      # Verified OSM line for NH-44 highway
├── frontend/
│   ├── src/
│   │   ├── app/                        # Next.js App Router (Dashboard, Simulation, Admin, Validation)
│   │   ├── components/                 # Leaflet Map, KPI Cards, Recharts, Health Modal
│   │   ├── services/api.ts             # Typed REST API client
│   │   └── types/flood.ts              # Shared TypeScript definitions
│   └── package.json
├── infrastructure/
│   ├── Dockerfile.backend              # Production Python container
│   ├── Dockerfile.frontend             # Multi-stage Next.js container
│   └── postgis-init/01_init.sql        # Spatial database schema
├── docs/
│   ├── ARCHITECTURE.md                 # System design & component diagrams
│   ├── DATA_SOURCES.md                 # Data catalog & provenance rules
│   ├── MODEL_METHODOLOGY.md            # Hydrology & nowcasting mathematics
│   ├── API_DOCUMENTATION.md            # REST API specifications
│   ├── DEPLOYMENT.md                   # Local, Docker, & Cloud deployment
│   ├── VALIDATION.md                   # Ground-truth validation framework
│   └── LIMITATIONS.md                  # System assumptions & boundaries
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 📋 Scientific Integrity Guarantees

1. **No Fake Sensors**: The platform never simulates fictitious water-level or rainfall sensors as real observations.
2. **Terrain Susceptibility Fallback**: Sub-surface drainage data is clearly marked as `NOT_AVAILABLE`. The system transparently runs in Terrain + Land-Cover Runoff Susceptibility Mode until surveyed pipe networks are imported.
3. **SWMM Hydraulic Decoupling**: The EPA SWMM engine remains dormant until an official `.inp` model file is uploaded.
4. **Validation Honesty**: When zero ground-truth validation events exist, the system strictly reports `INSUFFICIENT_GROUND_TRUTH` rather than displaying ungrounded accuracy percentages.
