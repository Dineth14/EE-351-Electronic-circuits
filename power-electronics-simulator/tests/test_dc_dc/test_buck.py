"""Tests for buck converter."""

from __future__ import annotations

import numpy as np
from numpy.testing import assert_allclose

from power_electronics.converters.dc_dc.buck import BuckConverter


def test_buck_instantiation(dc_dc_params):
    conv = BuckConverter(dc_dc_params)
    assert conv is not None


def test_buck_simulation(dc_dc_params):
    conv = BuckConverter(dc_dc_params)
    result = conv.simulate(0.02, 5000)
    for key in ["Vin", "Vout", "IL", "IC", "Iout", "Q_gate", "D_current", "power_dissipation"]:
        assert key in result.signals
        assert len(result.signals[key]) == len(result.time)
        assert np.all(np.isfinite(result.signals[key]))
    assert result.metrics["output_power_W"] >= 0


def test_buck_theoretical(dc_dc_params):
    conv = BuckConverter(dc_dc_params)
    result = conv.simulate(0.05, 8000)
    th = conv.get_theoretical_values()["Vout_avg"]
    sim = float(np.mean(result.signals["Vout"][-2000:]))
    assert_allclose(sim, th, rtol=0.02)
    assert conv.get_theoretical_values()["Vout_avg"] > 0
    assert isinstance(conv.get_param_schema(), dict)
