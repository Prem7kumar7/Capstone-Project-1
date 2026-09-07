# Scientific Validation Framework

## Overview

A core requirement of the SIH 2026 problem statement and good scientific engineering is strict honesty regarding model accuracy.

> **Integrity Rule**: Never display &ldquo;95% accurate&rdquo; or fabricate statistical confidence numbers unless calculated directly from an empirical ground-truth dataset.

---

## 1. Ground-Truth Data Ingestion

Validation events must represent verified field occurrences:
- Date and timestamp of observation
- Spatial coordinates (lat/lon)
- 24-hour observed rainfall depth ($\text{mm}$)
- Prediction lead time ($\text{hours}$)
- Observed flooded status ($\text{True} / \text{False}$)
- Measured water depth ($m$) from ultrasonic gauges or municipal water-level boards
- Source of ground-truth evidence (e.g., DDMA Kapurthala official report, campus security log)

Observations can be registered via `POST /api/v1/validation/record-observation`.

---

## 2. Calculated Scientific Metrics

When verified field events are logged, the system automatically computes:

### A. Classification Metrics (Flood vs. No Flood)
- **True Positives (TP)**: Model predicted flood, location flooded.
- **False Positives (FP)**: Model predicted flood, location did not flood.
- **True Negatives (TN)**: Model predicted normal, location did not flood.
- **False Negatives (FN)**: Model predicted normal, location flooded.
- **Precision**: $\frac{TP}{TP + FP}$
- **Recall**: $\frac{TP}{TP + FN}$
- **F1 Score**: $2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$

### B. Water Depth Error Metrics (Continuous)
- **Mean Absolute Error (MAE)**:
  $$\text{MAE} = \frac{1}{N} \sum_{i=1}^N |y_{\text{pred}, i} - y_{\text{obs}, i}|$$
- **Root Mean Squared Error (RMSE)**:
  $$\text{RMSE} = \sqrt{\frac{1}{N} \sum_{i=1}^N (y_{\text{pred}, i} - y_{\text{obs}, i})^2}$$

---

## 3. Policy on Empty Datasets

When the event count is 0, the API returns:
```json
{
  "validation_status": "INSUFFICIENT_GROUND_TRUTH",
  "total_events_recorded": 0,
  "message": "Validation dataset insufficient (0 ground-truth observations recorded). Sensor or manual observation logs required to compute scientific accuracy metrics. No synthetic validation accuracy is fabricated."
}
```
The frontend explicitly communicates this state to operators and evaluators.
