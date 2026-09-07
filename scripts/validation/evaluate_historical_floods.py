"""
Evaluates model flood predictions against authoritative satellite flood observations
(ISRO/NRSC NDEM & Sentinel-1 SAR July 2023 Punjab Floods).
"""
import json
from pathlib import Path

event_path = Path("data/sample_events/punjab_floods_july2023.json")
if not event_path.exists():
    print("Event data not found.")
    exit(1)

data = json.loads(event_path.read_text())
pts = data.get("ground_truth_validation_points", [])

tp, fp, tn, fn = 0, 0, 0, 0
for pt in pts:
    pred = pt["predicted_risk_score"] >= 50.0
    obs = pt["observed_flooded"]
    if pred and obs:
        tp += 1
    elif pred and not obs:
        fp += 1
    elif not pred and not obs:
        tn += 1
    else:
        fn += 1

precision = tp / max(tp + fp, 1)
recall = tp / max(tp + fn, 1)
f1 = (2 * precision * recall) / max(precision + recall, 0.001)
iou = tp / max(tp + fp + fn, 1)

print(f"=== SATELLITE VALIDATION: {data['event_id']} ===")
print(f"Source: {data['source_organization']}")
print(f"Total Points: {len(pts)} | TP: {tp} | FP: {fp} | TN: {tn} | FN: {fn}")
print(f"Precision: {precision:.2f} ({precision*100:.1f}%)")
print(f"Recall:    {recall:.2f} ({recall*100:.1f}%)")
print(f"F1 Score:  {f1:.2f}")
print(f"IoU:       {iou:.2f} ({iou*100:.1f}%)")
