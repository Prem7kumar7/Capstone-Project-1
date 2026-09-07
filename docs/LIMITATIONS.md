# System Limitations & Operational Boundaries

Scientific transparency requires documenting the assumptions, limitations, and operational boundaries of this platform.

---

## 1. Sub-Surface Drainage Network Data

- **Current State**: Detailed engineering surveys of underground storm sewer conduits, pipe diameters, invert elevations, manhole drop structures, and pump operational curves for the LPU campus and adjacent NH-44 highway are **currently unavailable**.
- **System Behavior**: Rather than generating synthetic pipe geometries, the system explicitly reports drainage data as `NOT_AVAILABLE`.
- **Operational Mode**: Runs in **Simplified Runoff & Terrain Susceptibility Mode** based on SCS-CN and Copernicus DEM depression analysis.
- **Path Forward**: University facilities or municipal engineering departments can import surveyed drainage network files (`.inp`) to activate the EPA SWMM 1D/2D hydraulic coupler.

---

## 2. Weather Radar & Nowcasting Ingestion

- **Current State**: Direct polar volume reflectivity feeds ($dBZ$) from the nearest India Meteorological Department (IMD) Doppler Weather Radars (e.g. IMD Patiala or Amritsar) are not currently accessible via public open API.
- **System Behavior**: Short-term precipitation forecasts are driven by the Open-Meteo NWP multi-model blend (ECMWF IFS 9km / GFS 13km), supplemented by Eulerian persistence decay models.
- **Spatial Resolution**: Global NWP models have a grid resolution of 9–13 km, which is coarse for hyper-local convective cloudbursts (< 2 km).
- **Path Forward**: The platform includes a decoupled **Advanced Spatial Nowcasting Module** (`backend/app/advanced_nowcasting/`) with 2D optical flow advection algorithms that will immediately become operational once high-resolution radar or satellite raster grids are ingested.

---

## 3. Flood Risk Score vs. Calibrated Probability

- **Terminology**: The platform outputs a **Flood Risk Score (0–100)**, which is an engineering composite index.
- **Limitation**: This score should **not** be interpreted as an empirical or frequentist flood probability percentage until the system is calibrated against multi-year local gauge observations.
- **Weights**: Factor weights (Rainfall: 50%, Topography: 25%, Drainage: 15%, Imperviousness: 10%) are based on standard hydrological engineering guidelines and can be calibrated via `config/hydrology_params.json`.

---

## 4. Water Depth Bracket Estimates

- **Labeling**: All predicted inundation depths (< 0.10 m, 0.10–0.30 m, 0.30–0.50 m, 0.50–1.00 m, > 1.00 m) are strictly **MODEL ESTIMATES**.
- **Limitation**: In the absence of physical ultrasonic or pressure-transducer water-level sensors installed in campus underpasses and swales, depths are calculated mathematically from SCS-CN surface runoff volume and depression geometry, not measured directly.

---

## 5. Model Validation Data Sufficiency

- **Current State**: No verified sensor time-series or municipal flood logs are pre-populated in the database.
- **System Behavior**: The validation API explicitly returns `validation_status: "INSUFFICIENT_GROUND_TRUTH"`.
- **Policy**: The system refuses to display manufactured accuracy figures (such as &ldquo;95% accuracy&rdquo;) to preserve scientific honesty during academic and hackathon evaluations.
