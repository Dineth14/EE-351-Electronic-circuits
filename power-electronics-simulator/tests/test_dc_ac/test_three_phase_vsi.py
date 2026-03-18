"""Tests for three-phase VSI."""

from __future__ import annotations

import numpy as np

from power_electronics.converters.dc_ac.three_phase_vsi import ThreePhaseVSI


def test_three_phase_vsi_instantiation(dc_ac_params):
    conv = ThreePhaseVSI(dc_ac_params)
    assert conv is not None


def test_three_phase_vsi_simulation(dc_ac_params):
    conv = ThreePhaseVSI(dc_ac_params)
    result = conv.simulate(0.08, 2500)
    for key in ["Va", "Vb", "Vc", "Vab", "Vbc", "Vca", "Ia", "Ib", "Ic", "Q1", "Q6"]:
        assert key in result.signals
        assert len(result.signals[key]) == len(result.time)
        assert np.all(np.isfinite(result.signals[key]))
    assert result.metrics["fundamental_V"] > 0
    assert conv.get_theoretical_values()["fundamental_phase_peak"] > 0
    assert isinstance(conv.get_param_schema(), dict)
