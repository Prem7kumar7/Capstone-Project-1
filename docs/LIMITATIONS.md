# System Limitations & Engineering Constraints

In compliance with academic rigor and the SIH 2026 problem statement guidelines, this document transparently discloses all technical limitations, data constraints, and model assumptions.

---

## 1. Drainage Network Limitations
1. **Absence of Private Engineering Drawings**: Sub-surface stormwater sewer pipe diameters, invert levels, and manhole coordinates are not publicly exposed by municipal authorities. The system does not invent synthetic pipes.
2. **Simplified Surface Limitation**: Operational flood risk is computed via surface accumulation and depression overflow rather than a fully dynamic Saint-Venant hydraulic network.
3. **Dormant SWMM Interface**: The EPA SWMM coupler is architecturally ready but remains dormant until an official `.inp` network model is imported.

---

## 2. Weather & Precipitation Resolution
1. **Spatial Resolution of NWP**: Open-Meteo NWP precipitation blends (ECMWF/DWD/GFS) have a grid cell resolution of 7–11 km. Highly localized hyper-convective microbursts (< 2 km) may exhibit spatial smoothing.
2. **Doppler Radar Access**: Public Doppler Weather Radar (DWR) polar volume CAPPI data from IMD is not currently accessible via open unauthenticated REST API. The optical flow advection module is architecturally implemented and awaits a direct radar data feed.

---

## 3. Topographic DEM Resolution
1. **Copernicus DEM 30m**: Elevation analysis operates on a 30m grid. Sub-meter curb-heights, road saucer drains, and micro-embankments are smoothed within the 30m cell average.
2. **High-Accuracy Drone/LiDAR Potential**: For centimeter-grade flood inundation modelling, a drone photogrammetric or LiDAR survey (< 1m resolution) would be required.

---

## 4. Uncalibrated Flood Risk Score
1. **Not a Statistical Probability**: The **Flood Risk Score (0–100)** is an engineering composite susceptibility index combining rainfall intensity, cumulative depth, terrain depression index, and impervious fraction. It must not be cited as a calibrated probability of flooding.
2. **Estimated Depth & Time**: Water depth brackets (e.g. `0.30 - 0.60 m`) and time-to-flood are model estimates derived from SCS runoff accumulation, not direct ultrasonic sensor telemetry.

---

## 5. Satellite Flood Validation Resolution
1. **Revisit Cadence**: Synthetic Aperture Radar (Sentinel-1 SAR) has an orbital repeat cycle of 6–12 days. Historical validation is conducted on major disaster passes (July 2023 Punjab floods) rather than sub-hourly urban flash-flood cycles.
