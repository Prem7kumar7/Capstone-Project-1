from typing import Dict, Any, List

class ConvLSTMNowcastingInterface:
    """
    Interface Specification for Deep Learning Spatial Nowcasting (ConvLSTM / PredRNN).
    
    Strict Scientific Honesty:
    - Deep learning nowcasting models CANNOT be claimed as operational without 
      actual radar reflectivity tensor datasets (e.g. IMD Patiala/Amritsar DWR 
      Level-2 polar volume data) and substantial GPU training.
    - This interface documents the required contract and returns status: AWAITING_TRAINING_DATA.
    """
    def __init__(self):
        self.model_architecture = "Convolutional LSTM (ConvLSTM2D)"
        self.tensor_input_shape = (None, 6, 128, 128, 1)  # (Batch, Timesteps=6 (1 hour at 10-min interval), H=128, W=128, Channels=1 dBZ)
        self.tensor_output_shape = (None, 6, 128, 128, 1) # Next 6 frames (1-hour lead time)

    def get_prerequisites(self) -> Dict[str, Any]:
        return {
            "model_type": self.model_architecture,
            "status": "NON_OPERATIONAL_PROTOTYPE_SPECIFICATION",
            "is_trained": False,
            "data_requirements": [
                "Continuous Doppler Weather Radar (DWR) dBZ reflectivity grids (minimum 2 years of monsoon data)",
                "Spatial resolution: 1 km x 1 km or higher",
                "Temporal cadence: 10 minutes",
                "Precipitation Marshall-Palmer Z-R conversion parameters: Z = 200 * R^1.6"
            ],
            "operational_status": "Dormant. The system currently utilizes the NWP point forecast and Eulerian persistence models for live operations."
        }

convlstm_spec = ConvLSTMNowcastingInterface()
