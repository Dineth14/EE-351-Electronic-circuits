"""Tests for three-phase full-bridge rectifier."""

from __future__ import annotations

import numpy as np

from power_electronics.converters.ac_dc.three_phase_bridge import ThreePhaseBridgeRectifier


def test_three_phase_bridge_instantiation(ac_dc_params):
    conv = ThreePhaseBridgeRectifier(ac_dc_params)
    assert conv is not None


def test_three_phase_bridge_simulation(ac_dc_params):
    conv = ThreePhaseBridgeRectifier(ac_dc_params)
    result = conv.simulate(0.2, 4000)
    for key in ["Va", "Vb", "Vc", "Vdc_raw", "Vdc_filtered", "Iload"]:
        assert key in result.signals
    for name, arr in result.signals.items():
        if isinstance(arr, np.ndarray) and arr.ndim == 1:
            assert len(arr) == len(result.time)
            assert np.all(np.isfinite(arr))
    assert result.metrics["Vdc_avg"] > 0
    assert result.converter_name == "three_phase_bridge"


def test_three_phase_bridge_theoretical(ac_dc_params):
    conv = ThreePhaseBridgeRectifier(ac_dc_params)
    th = conv.get_theoretical_values()["Vdc_avg"]
    assert th > 0
    assert isinstance(conv.get_param_schema(), dict)
    assert conv.get_info().category == "AC-DC"


def test_three_phase_bridge_diode_states(ac_dc_params):
    conv = ThreePhaseBridgeRectifier(ac_dc_params)
    result = conv.simulate(0.2, 4000)
    ds = result.signals["diode_states"]
    assert ds.shape == (4000, 6)
