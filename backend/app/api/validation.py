import uuid
import math
from fastapi import APIRouter
from typing import List, Dict, Any
from datetime import datetime, timezone
from backend.app.schemas.validation import ValidationEventCreate, ValidationEventResponse, ValidationMetricsResponse
from backend.app.utils.geo import utc_to_ist_str

router = APIRouter(prefix="/validation", tags=["Scientific Validation"])

# In-memory storage for genuine validation events (persists during runtime)
VERIFIED_VALIDATION_EVENTS: List[Dict[str, Any]] = []

@router.get("/metrics", response_model=ValidationMetricsResponse)
def get_validation_metrics():
    """
    Returns scientific validation metrics.
    
    CRITICAL SCIENTIFIC HONESTY:
    Never invents fake accuracy percentages.
    If no verified ground-truth events have been recorded, explicitly reports:
    'Validation dataset insufficient (0 ground-truth observations recorded)'.
    """
    total = len(VERIFIED_VALIDATION_EVENTS)

    if total == 0:
        return {
            "validation_status": "INSUFFICIENT_GROUND_TRUTH",
            "total_events_recorded": 0,
            "message": "Validation dataset insufficient (0 ground-truth observations recorded). Sensor or manual observation logs required to compute scientific accuracy metrics. No synthetic validation accuracy is fabricated.",
            "metrics": None,
            "events": []
        }

    # If genuine observations exist, calculate true scientific metrics
    tp, fp, tn, fn = 0, 0, 0, 0
    depth_errors = []

    for ev in VERIFIED_VALIDATION_EVENTS:
        pred_flood = ev["predicted_risk_score"] >= 50.0
        obs_flood = ev["observed_flooded"]

        if pred_flood and obs_flood:
            tp += 1
        elif pred_flood and not obs_flood:
            fp += 1
        elif not pred_flood and not obs_flood:
            tn += 1
        else:
            fn += 1

        if ev.get("observed_depth_m") is not None and ev.get("predicted_depth_m") is not None:
            depth_errors.append(abs(ev["predicted_depth_m"] - ev["observed_depth_m"]))

    precision = round(tp / max(tp + fp, 1), 2)
    recall = round(tp / max(tp + fn, 1), 2)
    f1 = round((2 * precision * recall) / max(precision + recall, 0.001), 2)
    mae_depth = round(sum(depth_errors) / max(len(depth_errors), 1), 3) if depth_errors else None
    rmse_depth = round(math.sqrt(sum([e**2 for e in depth_errors]) / max(len(depth_errors), 1)), 3) if depth_errors else None

    metrics = {
        "confusion_matrix": {"true_positive": tp, "false_positive": fp, "true_negative": tn, "false_negative": fn},
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "depth_mae_m": mae_depth,
        "depth_rmse_m": rmse_depth
    }

    event_responses = []
    for ev in VERIFIED_VALIDATION_EVENTS:
        event_responses.append({
            "id": ev["id"],
            "event_timestamp_utc": ev["event_timestamp_utc"],
            "location_name": ev["location_name"],
            "coordinates": [ev["longitude"], ev["latitude"]],
            "observed_rainfall_24h_mm": ev["observed_rainfall_24h_mm"],
            "predicted_risk_score": ev["predicted_risk_score"],
            "observed_flooded": ev["observed_flooded"],
            "predicted_depth_bracket": ev["predicted_depth_bracket"],
            "observed_depth_bracket": ev.get("observed_depth_bracket"),
            "ground_truth_source": ev["ground_truth_source"],
            "status": "VERIFIED_OBSERVATION"
        })

    return {
        "validation_status": "VALIDATED" if total >= 5 else "PARTIALLY_VALIDATED",
        "total_events_recorded": total,
        "message": f"Calculated based on {total} genuine ground-truth observation records.",
        "metrics": metrics,
        "events": event_responses
    }

@router.post("/record-observation")
def record_ground_truth_observation(ev: ValidationEventCreate):
    """
    Allows university emergency management, municipal officials, or automated water-level sensors
    to log genuine ground-truth flood observations for backtesting and validation.
    """
    now_utc = datetime.now(timezone.utc)
    ev_id = f"VAL-{now_utc.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    record = {
        "id": ev_id,
        "event_timestamp_utc": now_utc.isoformat(),
        "study_area_id": ev.study_area_id,
        "location_name": ev.location_name,
        "latitude": ev.latitude,
        "longitude": ev.longitude,
        "observed_rainfall_24h_mm": ev.observed_rainfall_24h_mm,
        "peak_intensity_mm_h": ev.peak_intensity_mm_h,
        "lead_time_hours": ev.lead_time_hours,
        "predicted_risk_score": ev.predicted_risk_score,
        "predicted_risk_category": ev.predicted_risk_category,
        "predicted_depth_bracket": ev.predicted_depth_bracket,
        "predicted_depth_m": ev.predicted_depth_m,
        "observed_flooded": ev.observed_flooded,
        "observed_depth_m": ev.observed_depth_m,
        "observed_depth_bracket": ev.observed_depth_bracket,
        "ground_truth_source": ev.ground_truth_source,
        "notes": ev.notes,
        "verified_by": ev.verified_by
    }

    VERIFIED_VALIDATION_EVENTS.append(record)

    return {
        "status": "SUCCESS",
        "event_id": ev_id,
        "message": "Genuine validation observation successfully registered.",
        "total_events_in_db": len(VERIFIED_VALIDATION_EVENTS)
    }
