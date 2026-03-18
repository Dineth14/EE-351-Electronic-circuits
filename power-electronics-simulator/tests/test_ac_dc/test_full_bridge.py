"""Tests for full-bridge rectifier."""

from __future__ import annotations

import numpy as np
from numpy.testing import assert_allclose

from power_electronics.converters.ac_dc.full_bridge import FullBridgeRectifier


def test_full_bridge_instantiation(ac_dc_params):
    conv = FullBridgeRectifier(ac_dc_params)
    assert conv is not None


def test_full_bridge_simulation_structure(ac_dc_params):
    conv = FullBridgeRectifier(ac_dc_params)
    result = conv.simulate(0.2, 4000)
    for key in ["Vout_raw", "Vout_filtered", "ID1", "ID2", "ID3", "ID4"]:
        assert key in result.signals
    for arr in result.signals.values():
        if isinstance(arr, np.ndarray) and arr.ndim == 1:
            assert len(arr) == len(result.time)
            assert np.all(np.isfinite(arr))
    assert result.metrics["Vdc_avg"] > 0


def test_full_bridge_theoretical_close(ac_dc_params):
    conv = FullBridgeRectifier(ac_dc_params)
    result = conv.simulate(0.3, 6000)
    th = conv.get_theoretical_values()["Vdc_avg"]
    sim = float(np.mean(result.signals["Vdc_raw"]))
    assert_allclose(sim, th, rtol=0.02)
    assert conv.get_theoretical_values()["Vdc_avg"] > 0
    assert isinstance(conv.get_param_schema(), dict)
