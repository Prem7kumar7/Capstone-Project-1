# Data Availability Report: SIH26085 Urban Flood Nowcasting System

## Executive Summary
This mandatory report classifies all datasets relevant to the Urban Flood Nowcasting System for **Lovely Professional University (LPU), Chaheru, Phagwara, and Jalandhar** into five strict categories in compliance with the **Zero-Fabrication Scientific Rule**.

---

### 1. AVAILABLE (Acquired, Verified & Integrated)
1. **Open-Meteo Global NWP Precipitation API**: Real-time precipitation rate (mm/h) and 0-6 hour forecast.
2. **Copernicus DEM GLO-30 Elevation**: Authoritative 30m Digital Elevation Model covering 230m to 255m MSL across the study corridor.
3. **OpenStreetMap Verified Study Area Boundaries**:
   - Lovely Professional University Campus (Way 422435593)
   - Chaheru / Chiheru Railway & Drainage Corridor
   - Municipal Corporation Phagwara Urban Basin
   - Municipal Corporation Jalandhar Urban Metro
4. **National Highway 44 (NH-44 / GT Road)**: Verified vector trunk polyline passing LPU main gates and Chaheru bridge.
5. **Regional Receiving Waterways**:
   - Chaheru Stream / Nullah
   - Phagwara Choe (Stormwater Outfall Channel)
   - Kala Sanghian Drain (Jalandhar Outfall)
   - Kali Bein River (Regional Receiving Basin)
6. **Critical Civic Infrastructure**:
   - Uni-Hospital (LPU Campus)
   - Civil Hospital Phagwara & Civil Hospital Jalandhar
   - Chaheru, Phagwara, and Jalandhar City Railway Stations
   - Rama Mandi Emergency Fire Sub-Station
7. **Satellite-Observed Flood Inundation (July 2023 Punjab Floods)**:
   - Documented ground-truth points from ISRO/NRSC Disaster Management Support Programme (DMSP) and Copernicus Sentinel-1 SAR C-band passes.

---

### 2. PARTIALLY AVAILABLE (Surface Drainage Only)
- **Open Surface Stormwater Channels & Roadside Saucer Drains**:
  - Surface drain geometry along NH-44 and major municipal roads is mapped in OpenStreetMap.
  - Channel alignments from Punjab Water Resources Department are verified.
  - **Limitation**: Cross-sectional hydraulic dimensions (manning's roughness, bottom width, side slope) are estimated using Indian Road Congress (IRC:SP:42) guidelines.

---

### 3. UNAVAILABLE (Not Publicly Accessible — Zero Fabrication)
- **Sub-Surface Storm Sewer Network Engineering Drawings**:
  - Pipe diameters (mm)
  - Pipe invert elevations (m MSL)
  - Manhole chamber depths and coordinates
  - Pumping station operational telemetry (discharge in cusecs)
- **Status Declaration**:
  - Municipal Corporation Jalandhar, Municipal Corporation Phagwara, and LPU Estate maintain sub-surface drainage drawings privately; they are not published as open GIS/WFS services.
  - **Resolution**: The system does NOT invent synthetic pipe networks. It operates in **Level 1 (Topographic DEM flow accumulation)** and **Level 2 (Mapped surface channels)**, while maintaining a dormant EPA SWMM interface (Level 3) that activates only when official `.inp` files are supplied.

---

### 4. DERIVED (Scientifically Defensible Derived Layers)
- **Topographic Slope**: Derived from Copernicus DEM 30m elevation gradients via central difference approximation.
- **Depression Storage Index**: Derived by comparing local elevation against surrounding 30m neighbourhood cells to isolate water-pooling depressions.
- **SCS Curve Number (CN)**: Derived from standard USDA NRCS National Engineering Handbook (Part 630) and Central Water Commission (CWC) tables for Alluvial Silt Loam (Hydrologic Soil Group B).
- **Runoff Depth (Q)**: Calculated via standard SCS-CN equation with initial abstraction ratio lambda = 0.20 (and configurable lambda = 0.05 for Indian conditions).
- **0–6h Dampened Trend Nowcast**: Derived by extrapolating 15-minute rainfall derivative dR/dt with polynomial time-dampening 1 / (1 + 0.5 * t_lead).

---

### 5. SIMULATED (Clearly Labeled Demo Scenarios)
- **What-If Scenario Simulator (`/simulation`)**:
  - Allows university administrators and emergency responders to test synthetic cloudburst intensities (10 to 150 mm/h) and pipe clogging percentages (0% to 100%).
  - Every simulated output is flagged with `execution_mode: SIMULATED` and prominent amber banners to prevent confusion with real-time operations.
