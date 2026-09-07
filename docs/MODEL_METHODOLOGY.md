# Hydrological, Hydraulic & Nowcasting Model Methodology

## SIH26085 – Urban Flood Nowcasting System

---

### 1. Rainfall Nowcasting Pipeline (0–6 Hours)

#### A. Persistence Decay Baseline
$$R_{persist}(t) = R_0 \cdot e^{-\alpha t}$$
Where $R_0$ is the current observed precipitation intensity (mm/h), $\alpha = 0.15$ is the decay constant, and $t$ is the forecast lead time in hours.

#### B. Dampened Statistical Trend Extrapolation
$$\frac{dR}{dt} = \frac{R_{recent} - R_{prior}}{\Delta t}$$
$$R_{trend}(t) = \max\left(0, R_0 + \frac{dR}{dt} \cdot t \cdot \frac{1}{1 + 0.5 \cdot t}\right)$$
The polynomial dampening factor $\frac{1}{1 + 0.5 \cdot t}$ prevents runaway linear divergence at longer forecast horizons (4–6 hours).

---

### 2. SCS-CN Rainfall-Runoff Model

Direct runoff depth $Q$ (mm) is computed using the USDA NRCS Curve Number method:
$$S = \frac{25400}{CN} - 254$$
$$I_a = \lambda \cdot S$$
$$Q = \begin{cases} \frac{(P - I_a)^2}{P - I_a + S}, & \text{if } P > I_a \\ 0, & \text{if } P \le I_a \end{cases}$$
Where:
- $P$ is cumulative rainfall (mm).
- $S$ is potential maximum soil retention (mm).
- $I_a$ is initial abstraction (mm).
- $\lambda = 0.20$ (default USDA NRCS) or $\lambda = 0.05$ (recommended by Central Water Commission for Indian semi-arid/alluvial basins).

---

### 3. Topographic Analysis (Copernicus DEM 30m)

#### Slope Angle:
$$\text{Slope} (\text{degrees}) = \arctan\left(\frac{\Delta z}{d}\right) \cdot \frac{180}{\pi}$$

#### Depression Storage Index:
$$D = \max(0, \bar{z}_{surrounding} - z_{center})$$
Points where $z_{center} < \bar{z}_{surrounding}$ are categorized as natural depressions prone to ponding.

---

### 4. Composite Flood Risk Score (0–100)

The composite index combines meteorological, hydrological, and topographic parameters:
$$\text{FRS} = w_1 \cdot S_{rain} + w_2 \cdot S_{cum} + w_3 \cdot S_{dep} + w_4 \cdot S_{drain} + w_5 \cdot S_{imp}$$
Where weights are configured in `config/hydrology_params.json`:
- $w_1 = 0.30$ (Forecast Rainfall Intensity)
- $w_2 = 0.20$ (Cumulative Rainfall)
- $w_3 = 0.25$ (Terrain Depression Index)
- $w_4 = 0.15$ (Drainage Inadequacy Proxy)
- $w_5 = 0.10$ (Impervious Fraction)
