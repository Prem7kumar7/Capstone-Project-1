import json
from pathlib import Path
from typing import Dict, Any
from backend.app.config import settings
from backend.app.utils.logging import logger

CONFIG_FILE_PATH = settings.BASE_DIR_PATH / "config" / "hydrology_params.json"

class HydrologyConfigManager:
    _instance = None
    _config: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(HydrologyConfigManager, cls).__new__(cls)
            cls._instance.load_config()
        return cls._instance

    def load_config(self) -> Dict[str, Any]:
        if not CONFIG_FILE_PATH.exists():
            logger.warning(f"Hydrology config file not found at {CONFIG_FILE_PATH}. Using fallback defaults.")
            self._config = self._get_fallback_defaults()
            return self._config
        try:
            with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
                self._config = json.load(f)
                logger.info(f"Loaded hydrology configuration v{self._config.get('version', 'unknown')}")
        except Exception as e:
            logger.error(f"Error reading hydrology config: {e}. Falling back to defaults.")
            self._config = self._get_fallback_defaults()
        return self._config

    def get_config(self) -> Dict[str, Any]:
        if not self._config:
            self.load_config()
        return self._config

    def update_config(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        current = self.get_config()
        for k, v in updates.items():
            if v is not None:
                current[k] = v
        # Save back to file
        try:
            with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(current, f, indent=2)
            logger.info("Hydrology configuration successfully updated.")
        except Exception as e:
            logger.error(f"Failed to persist updated hydrology config: {e}")
        self._config = current
        return self._config

    def get_cn(self, land_cover_type: str) -> int:
        cns = self.get_config().get("curve_numbers", {})
        if land_cover_type in cns:
            return cns[land_cover_type]["cn_value"]
        return 85  # Default composite CN

    def get_lambda(self) -> float:
        return float(self.get_config().get("initial_abstraction_ratio_lambda", 0.20))

    def _get_fallback_defaults(self) -> Dict[str, Any]:
        return {
            "version": "1.0.0-fallback",
            "soil_hydrologic_group": "B",
            "initial_abstraction_ratio_lambda": 0.20,
            "curve_numbers": {
                "impervious_paved_roof": {"cn_value": 98, "impervious_fraction": 1.0},
                "academic_complex": {"cn_value": 92, "impervious_fraction": 0.85},
                "hostel_residential": {"cn_value": 79, "impervious_fraction": 0.65},
                "open_lawns_parks": {"cn_value": 69, "impervious_fraction": 0.15},
                "agricultural_fringe": {"cn_value": 72, "impervious_fraction": 0.05}
            },
            "manning_roughness": {
                "lined_storm_channel": 0.015,
                "overland_sheet_asphalt": 0.016
            },
            "rational_coefficients": {
                "impervious_roof": 0.90,
                "campus_pavement": 0.85,
                "lawns_permeable": 0.25
            },
            "risk_score_weights": {
                "forecast_rainfall_intensity": 0.30,
                "cumulative_rainfall": 0.20,
                "terrain_depression_index": 0.25,
                "drainage_inadequacy_proxy": 0.15,
                "impervious_fraction": 0.10
            }
        }

hydrology_config_manager = HydrologyConfigManager()
