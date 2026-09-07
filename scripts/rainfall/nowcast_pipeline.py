"""
Executes 0-6 hour nowcast comparison for a given rainfall scenario.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.app.nowcasting.persistence import PersistenceModel
from backend.app.nowcasting.trend import TrendExtrapolationModel

pm = PersistenceModel()
tm = TrendExtrapolationModel()

horizons = [0.25, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
current_intensity = 35.0 # mm/h
history = [15.0, 25.0, 35.0]

print(f"Current Intensity: {current_intensity} mm/h | History: {history}")
print(f"{'Horizon':<10} | {'Persistence (mm/h)':<20} | {'Trend Model (mm/h)':<20} | {'Confidence':<12}")
print("-" * 70)

for h in horizons:
    p = pm.predict(current_intensity, history, h)
    t = tm.predict(current_intensity, history, h)
    print(f"+{int(h*60) if h < 1 else int(h)} {'min' if h < 1 else 'hr':<4} | {p['projected_intensity_mm_h']:<20.2f} | {t['projected_intensity_mm_h']:<20.2f} | {t['confidence_score']:<12.2f}")
