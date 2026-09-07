import pytest
from backend.app.hydrology.swmm_coupler import swmm_coupler
from backend.app.advanced_nowcasting.advection_optical_flow import spatial_nowcaster
from backend.app.advanced_nowcasting.convlstm_interface import convlstm_spec
import numpy as np

def test_swmm_coupler_dormant_without_inp():
    status = swmm_coupler.get_engine_status()
    assert status["status"] == "DORMANT"
    assert status["is_active"] is False
    assert "Requires an official drainage network .inp file" in status["message"]

    sim_res = swmm_coupler.execute_simulation([])
    assert sim_res["success"] is False
    assert sim_res["fallback_mode"] == "SIMPLIFIED_RUNOFF_LIMITATION"

def test_spatial_nowcaster_feed_status():
    status = spatial_nowcaster.check_feed_status(radar_feed_connected=False)
    assert status["status"] == "AWAITING_RADAR_FEED"
    assert status["is_active"] is False

def test_spatial_advection_vector_calculation():
    # Synthetic 2D precipitation pattern moving East
    grid0 = np.zeros((32, 32))
    grid0[14:18, 10:14] = 25.0  # Center at (16, 12)

    grid1 = np.zeros((32, 32))
    grid1[14:18, 14:18] = 25.0  # Shifted 4 units to the right (u = +4)

    u, v = spatial_nowcaster.compute_advection_vector(grid0, grid1)
    assert u == pytest.approx(4.0, abs=1.0)
    assert v == pytest.approx(0.0, abs=1.0)

def test_convlstm_prerequisites_transparency():
    spec = convlstm_spec.get_prerequisites()
    assert spec["status"] == "NON_OPERATIONAL_PROTOTYPE_SPECIFICATION"
    assert spec["is_trained"] is False
    assert len(spec["data_requirements"]) > 0
