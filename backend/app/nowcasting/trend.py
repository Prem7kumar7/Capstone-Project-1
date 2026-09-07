import math
from typing import List, Dict, Any
from backend.app.nowcasting.base import BaseRainfallModel

class TrendExtrapolationModel(BaseRainfallModel):
    """
    Polynomial / Linear Trend Extrapolation Nowcasting Model.
    Computes rainfall trend rate dR/dt from recent historical steps and projects forward with dampening.
    """
    def __init__(self):
        super().__init__(model_name="TrendExtrapolationDampenedModel", model_version="1.1.0")

    def predict(
        self,
        current_intensity_mm_h: float,
        recent_history_mm: List[float],
        lead_time_hours: float
    ) -> Dict[str, Any]:
        if lead_time_hours < 0:
            lead_time_hours = 0.0

        if len(recent_history_mm) < 2:
            # Fall back to baseline if history is insufficient
            rate_change_per_hour = 0.0
        else:
            # Estimate linear trend from last 2-4 points
            recent = recent_history_mm[-4:]
            rate_change_per_hour = (recent[-1] - recent[0]) / max(len(recent) - 1, 1)

        # Dampen trend projection over time to avoid runaway linear growth
        dampening = 1.0 / (1.0 + 0.5 * lead_time_hours)
        projected = current_intensity_mm_h + (rate_change_per_hour * lead_time_hours * dampening)
        projected = max(0.0, projected)  # Rainfall cannot be negative

        confidence = max(0.15, 0.90 - (0.15 * lead_time_hours))

        return {
            "model_name": self.model_name,
            "model_version": self.model_version,
            "lead_time_hours": lead_time_hours,
            "projected_intensity_mm_h": round(projected, 2),
            "estimated_trend_slope": round(rate_change_per_hour, 3),
            "dampening_factor": round(dampening, 3),
            "confidence_score": round(confidence, 2),
            "model_category": "NWP_STATISTICAL_TREND"
        }
