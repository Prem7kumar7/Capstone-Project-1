# Hydrological & Nowcasting Model Methodology

This document outlines the scientific and mathematical formulations implemented in the Urban Flood Nowcasting System.

---

## 1. Rainfall-Runoff Modeling: USDA SCS Curve Number Method

The Soil Conservation Service (SCS) Curve Number method (USDA NRCS NEH Part 630) calculates direct surface runoff depth from cumulative storm rainfall.

### Potential Maximum Retention ($S$)
$$S = \frac{25400}{CN} - 254 \quad [\text{mm}]$$

Where $CN$ is the dimensionless Curve Number (scale 30 to 100), loaded from `config/hydrology_params.json`:
- Impervious Pavements & Roofs: $CN = 98$
- University Academic Complexes: $CN = 92$
- Residential Hostel Blocks: $CN = 79$
- Open Lawns & Landscaped Parks: $CN = 69$
- Agricultural Perimeter: $CN = 72$

### Initial Abstraction ($I_a$)
$$I_a = \lambda \cdot S \quad [\text{mm}]$$

Where $\lambda$ is the initial abstraction ratio:
- Standard USDA NRCS default: $\lambda = 0.20$
- Indian Central Water Commission (CWC) recommended standard for monsoonal saturation: $\lambda = 0.05$ (configurable in Admin Panel).

### Direct Runoff Depth ($Q$)
$$Q = \begin{cases} \frac{(P - I_a)^2}{P - I_a + S} & \text{for } P > I_a \\ 0 & \text{for } P \le I_a \end{cases}$$

### Total Runoff Volume ($V$)
$$V = \frac{Q}{1000} \cdot A \quad [\text{m}^3]$$
Where $A$ is the catchment surface area in square meters.

---

## 2. Peak Discharge: Rational Method

For urban stormwater conveyance estimation:
$$Q_{\text{peak}} = \frac{C \cdot I \cdot A}{360} \quad [\text{m}^3/\text{s}]$$

Where:
- $C$ = Dimensionless runoff coefficient (Paved: 0.85, Roofs: 0.90, Lawns: 0.25)
- $I$ = Rainfall intensity in $\text{mm/hr}$
- $A$ = Drainage area in hectares ($ha$)

---

## 3. Topographic Depression & Terrain Analysis

Digital Elevation Models (DEM) from Copernicus GLO-30 are processed for local slope gradient and depression storage:
$$\text{Slope} = \arctan\left(\frac{\Delta Z}{D}\right)$$
$$\text{Depression Drop} = \overline{Z}_{\text{neighborhood}} - Z_{\text{point}}$$

A cell is flagged as a **Depression Hotspot** if $\text{Depression Drop} > 0.5\text{ m}$, representing natural water accumulation basins (e.g. the NH-44 Underpass near LPU Gate 1).

---

## 4. Composite Flood Risk Score (0–100)

The **Flood Risk Score** is an uncalibrated engineering composite index that synthesizes five normalized hydrological factors:

$$\text{Risk Score} = \frac{\sum_{i=1}^5 w_i \cdot F_i}{\sum_{i=1}^5 w_i}$$

| Factor | Description | Weight ($w_i$) |
| :--- | :--- | :--- |
| $F_1$: Forecast Intensity | Normalized to $80\text{ mm/h}$ cloudburst baseline | 0.30 |
| $F_2$: Cumulative Rain | Normalized to $150\text{ mm}$ extreme storm baseline | 0.20 |
| $F_3$: Topography | Function of slope and depression drop $\Delta Z$ | 0.25 |
| $F_4$: Drainage Inadequacy | Function of conveyance capacity and clogging % | 0.15 |
| $F_5$: Imperviousness | Fraction of paved/built surface | 0.10 |

### Classification Scale:
- **0 – 20**: Very Low (Normal operating conditions)
- **20 – 40**: Low (Minor roadside puddles; monitoring)
- **40 – 60**: Moderate (Advisory condition; low points accumulating water)
- **60 – 80**: High (Significant waterlogging; underpass hazard)
- **80 – 100**: Extreme (Severe inundation; active road closure recommended)

---

## 5. Water Depth Bracket Estimation (MODEL ESTIMATE)

Calculated from SCS runoff depth adjusted for depression geometry:
- **$< 0.10\text{ m}$**: Ankle depth / sheet flow
- **$0.10 - 0.30\text{ m}$**: Curb height / passable by heavy vehicles
- **$0.30 - 0.50\text{ m}$**: Exhaust height / small sedans stranded
- **$0.50 - 1.00\text{ m}$**: Severe inundation / vehicles submerged
- **$> 1.00\text{ m}$**: Extreme danger / active rescue required

*Strict Labeling Rule: Always tagged as **MODEL ESTIMATE**.*

---

## 6. Estimated Time-to-Flood (ESTIMATED)

Estimated from the rate of water rise:
$$\Delta t_{\text{flood}} = \frac{D_{\text{threshold}} - D_{\text{current}}}{\text{Rate of Rise}}$$
Brackets: `0–30 min`, `30–60 min`, `1–2 hours`, `2–4 hours`, `4–6 hours`, `> 6 hours`.

*Strict Labeling Rule: Always tagged as **ESTIMATED**; never presented as an exact arrival time.*

---

## 7. Advanced Spatial Nowcasting: 2D Optical Flow Advection

For spatial precipitation grids, the advection vector $(\vec{u}, \vec{v})$ is calculated via 2D phase correlation in the frequency domain:
$$C(u, v) = \mathcal{F}^{-1}\left(\frac{\mathcal{F}(I_{t+\Delta t}) \cdot \mathcal{F}^*(I_t)}{|\mathcal{F}(I_{t+\Delta t}) \cdot \mathcal{F}^*(I_t)|}\right)$$

The peak of $C(u, v)$ indicates the spatial displacement of storm cells between consecutive radar/satellite scans. Semi-Lagrangian backward trajectory advection then projects the spatial rainfall grid forward over 0–6 hours.
