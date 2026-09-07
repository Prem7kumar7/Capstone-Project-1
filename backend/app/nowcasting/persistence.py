import math
from typing import List, Dict, Any
from backend.app.nowcasting.base import BaseRainfallModel

class PersistenceModel(BaseRainfallModel):
    """
    Persistence Baseline Nowcasting Model.
    Assumes current rainfall rate persists, modified by an empirical atmospheric decorrelation decay:
        R(t + dt) = R(t) * exp(-dt / tau)
    where tau is the Eulerian decorrelation timescale (typically ~2.5 hours for convective/monsoonal rain).
    """
    def __init__(self, tau_hours: float = 2.5):
        super().__init__(model_name="EulerianPersistenceDecayModel", model_version="1.0.0")
        self.tau_hours = tau_hours

    def predict(
        self,
        current_intensity_mm_h: float,
        recent_history_mm: List[float],
        lead_time_hours: float
    ) -> Dict[str, Any]:
        if lead_time_hours < 0:
            lead_time_hours = 0.0

        # Exponential decay factor
        decay = math.exp(-lead_time_hours / self.tau_hours)
        projected_rate = current_intensity_mm_h * decay

        # Confidence decays as lead time increases
        confidence = max(0.2, 0.95 - (0.12 * lead_time_hours))

        return {
            "model_name": self.model_name,
            "model_version": self.model_version,
            "lead_time_hours": lead_time_hours,
            "projected_intensity_mm_h": round(projected_rate, 2),
            "decay_factor": round(decay, 3),
            "confidence_score": round(confidence, 2),
            "model_category": "NWP_PERSISTENCE_BASELINE"
        }
