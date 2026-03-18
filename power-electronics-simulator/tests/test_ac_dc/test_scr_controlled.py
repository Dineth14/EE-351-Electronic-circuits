"""Tests for SCR controlled rectifiers."""

from __future__ import annotations

import numpy as np

from power_electronics.converters.ac_dc.scr_full_bridge import SCRFullBridgeRectifier
from power_electronics.converters.ac_dc.scr_half_wave import SCRHalfWaveRectifier


def test_scr_half_wave_behavior(ac_dc_params):
    conv = SCRHalfWaveRectifier(ac_dc_params)
    result = conv.simulate(0.2, 4000)
    assert "firing_pulse" in result.signals
    assert "alpha_marker" in result.signals
    assert np.all(np.isfinite(result.signals["Vout"]))
    assert result.metrics["Vdc_avg"] > 0


def test_scr_full_bridge_behavior(ac_dc_params):
    conv = SCRFullBridgeRectifier(ac_dc_params)
    result = conv.simulate(0.2, 4000)
    assert "firing_pulses" in result.signals
    assert len(result.signals["firing_pulses"]) == len(result.time)
    assert isinstance(conv.get_param_schema(), dict)
    assert conv.get_theoretical_values()["Vdc_avg"] > 0
