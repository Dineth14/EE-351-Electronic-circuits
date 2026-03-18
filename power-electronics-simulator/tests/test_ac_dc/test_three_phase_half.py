"""Tests for three-phase half-wave rectifier."""

from __future__ import annotations

import numpy as np
from numpy.testing import assert_allclose

from power_electronics.converters.ac_dc.three_phase_half import ThreePhaseHalfRectifier


def test_three_phase_half_instantiation(ac_dc_params):
    conv = ThreePhaseHalfRectifier(ac_dc_params)
    assert conv is not None


def test_three_phase_half_simulation(ac_dc_params):
    conv = ThreePhaseHalfRectifier(ac_dc_params)
    result = conv.simulate(0.2, 4000)
    for key in ["Va", "Vb", "Vc", "Vdc_raw", "Vdc_filtered", "Iload"]:
        assert key in result.signals
    for name, arr in result.signals.items():
        if isinstance(arr, np.ndarray) and arr.ndim == 1:
            assert len(arr) == len(result.time)
            assert np.all(np.isfinite(arr))
    assert result.metrics["Vdc_avg"] > 0
    assert result.converter_name == "three_phase_half"


def test_three_phase_half_theoretical(ac_dc_params):
    conv = ThreePhaseHalfRectifier(ac_dc_params)
    result = conv.simulate(0.3, 6000)
    th = conv.get_theoretical_values()["Vdc_avg"]
    assert th > 0
    assert isinstance(conv.get_param_schema(), dict)
    assert conv.get_info().category == "AC-DC"
