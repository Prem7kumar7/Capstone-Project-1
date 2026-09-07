from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseRainfallModel(ABC):
    """Abstract Base Class for 0-6 hour rainfall nowcasting models."""

    def __init__(self, model_name: str, model_version: str = "1.0.0"):
        self.model_name = model_name
        self.model_version = model_version

    @abstractmethod
    def predict(
        self,
        current_intensity_mm_h: float,
        recent_history_mm: List[float],
        lead_time_hours: float
    ) -> Dict[str, Any]:
        """
        Generates rainfall forecast for a given lead time (0 - 6 hours).
        """
        pass
