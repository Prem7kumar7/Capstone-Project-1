# System Architecture

## Overview

The **Urban Flood Nowcasting System for Lovely Professional University (LPU), Phagwara, Punjab** is an enterprise-grade, modular hydrological forecasting and disaster-management platform designed for the Smart India Hackathon (SIH 2026) problem statement:

> *"Urban Flood Nowcasting System through Dynamic Coupling of Rainfall Forecasts and Urban Drainage Network Models"*

The platform couples short-term numerical weather forecasts with digital elevation terrain analysis, data-driven hydrological runoff equations (SCS-CN and Rational Method), and a decoupled EPA SWMM hydraulic model interface.

---

## Architectural Principles

1. **Strict Data Transparency & Provenance**: Every data layer is tagged as `LIVE`, `FORECAST`, `HISTORICAL`, `DERIVED`, or `SIMULATED`.
2. **Zero Fabrication Policy**: No fake sensors, fictitious drainage pipes, or artificial validation numbers are generated. When ground truth is absent, the system explicitly reports data unavailability or runs in uncalibrated susceptibility mode.
3. **Decoupled Hydraulic Simulation**: Distinguishes the operational **Simplified Runoff & Terrain Susceptibility Model** from the **EPA SWMM Coupler** (which requires official surveyed `.inp` network models).
4. **Data-Driven Hydrology**: Soil groups, Curve Numbers ($CN$), initial abstraction ratios ($\lambda$), and roughness parameters ($n$) are externalized in `config/hydrology_params.json` and are modifiable at runtime via Admin APIs.
5. **Decoupled Spatial Nowcasting**: Point/grid NWP forecasts are separated from the **Advanced Spatial Nowcasting Module** (2D optical flow advection on radar grids).

---

## Layered System Architecture Diagram

```mermaid
flowchart TD
    subgraph DataSources ["External Providers & Ingestion Adapters"]
        OM[Open-Meteo Live API\nPrecipitation & NWP Forecast]
        DEM[Copernicus DEM GLO-30\nOpen-Meteo Elevation API]
        OSM[OpenStreetMap Verified GIS\nLPU Boundary & NH-44 Roads]
        RadarSat[Radar / Satellite Feed Interface\n(Awaiting Live DWR Feed)]
    end

    subgraph DataIntegrity ["Data Integrity & Health Monitor"]
        Health[Health & Latency Check]
        Provenance[Provenance Tagger\nLIVE / SIMULATED / DERIVED]
    end

    subgraph NowcastingEngine ["0–6h Rainfall Nowcasting (Extensible)"]
        NWP[Open-Meteo Hourly Blended Forecast]
        Persist[Persistence Decay Model R*exp(-t/tau)]
        Trend[Trend Extrapolation with Dampening]
        OptFlow[Advanced 2D Optical Flow Advection]
        ConvLSTM[ConvLSTM Tensor Interface Specification]
    end

    subgraph HydrologyPipeline ["Hydrological & Hydraulic Engines"]
        HydroConfig[Config: hydrology_params.json\nCN Table, lambda, Soil Groups]
        SCS[SCS-CN Runoff Calculation\nQ = (P-Ia)^2 / (P-Ia+S)]
        Rational[Rational Peak Discharge Q=C*I*A]
        Terrain[Terrain Analysis: Slope, TWI, Depressions]
        Simplified[Simplified Drainage Limitation Model\n(Active Operational Mode)]
        SWMM[EPA SWMM Hydraulic Coupler\n(Dormant awaiting .inp network)]
    end

    subgraph DecisionSupport ["Flood Risk & Emergency Decision Support"]
        RiskScore[Composite Flood Risk Score 0–100\n(Uncalibrated Engineering Index)]
        DepthEst[Estimated Inundation Depth Bracket\n<0.1m to >1m (MODEL ESTIMATE)]
        TimeEst[Estimated Time-to-Flood\n0-30m to >6h (ESTIMATED)]
        Alerts[Advisory Engine: Green, Yellow, Orange, Red]
    end

    subgraph BackendAPI ["FastAPI REST Engine & Persistence"]
        FastAPI[FastAPI Application Server]
        DB[(PostgreSQL + PostGIS\n/ SQLite Fallback)]
    end

    subgraph FrontendUI ["Next.js GIS Disaster Dashboard"]
        Map[Interactive Leaflet GIS Viewer]
        KPIs[KPI Cards & Risk Breakdown]
        Chart[0-6h Rainfall Nowcast Chart]
        Simulator[What-If Scenario Simulator]
        Admin[Hydrology Calibration Panel]
        Validation[Ground-Truth Empirical Validation]
    end

    DataSources --> DataIntegrity
    DataIntegrity --> NowcastingEngine
    NowcastingEngine --> HydrologyPipeline
    HydroConfig --> HydrologyPipeline
    HydrologyPipeline --> DecisionSupport
    DecisionSupport --> BackendAPI
    BackendAPI --> FrontendUI
```

---

## Component Interaction Workflow

1. **Weather Ingestion**: The `OpenMeteoProvider` queries real-time observations and 0–6 hour forecasts for LPU coordinates (`31.2533° N, 75.7033° E`). Responses are cached in-memory with a 15-minute TTL.
2. **Terrain & Soil Analysis**: Digital elevation models are queried from Copernicus DEM. Slopes, relative depression indices, and land-cover Curve Numbers are extracted.
3. **Runoff Calculation**: Direct runoff volume ($m^3$) is computed using SCS-CN with the configured abstraction ratio $\lambda$ (default 0.20 or 0.05).
4. **Risk Scoring**: The multi-factor engine synthesizes rainfall intensity, cumulative rainfall, terrain depressions, drainage limitation, and imperviousness into a **Flood Risk Score (0–100)**.
5. **Advisory Generation**: Active advisories are generated with actionable evacuation and diversion protocols.
6. **GIS Map Display**: Features are rendered on the Leaflet map with interactive point inspection.
