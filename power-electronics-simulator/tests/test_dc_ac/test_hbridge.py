"""Tests for single-phase H-bridge inverter."""

from __future__ import annotations

import numpy as np

from power_electronics.converters.dc_ac.single_phase_hbridge import SinglePhaseHBridgeVSI


def test_hbridge_instantiation(dc_ac_params):
    conv = SinglePhaseHBridgeVSI(dc_ac_params)
    assert conv is not None


def test_hbridge_simulation(dc_ac_params):
    conv = SinglePhaseHBridgeVSI(dc_ac_params)
    result = conv.simulate(0.1, 3000)
    for key in ["Vout", "Iout", "Q1", "Q2", "Q3", "Q4", "carrier_wave", "reference_wave"]:
        assert key in result.signals
        assert len(result.signals[key]) == len(result.time)
        assert np.all(np.isfinite(result.signals[key]))
    assert result.metrics["Vout_rms"] > 0
    assert conv.get_theoretical_values()["fundamental_V"] > 0
    assert isinstance(conv.get_param_schema(), dict)
