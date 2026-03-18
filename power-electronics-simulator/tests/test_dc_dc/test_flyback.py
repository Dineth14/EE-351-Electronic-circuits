"""Tests for flyback converter."""

from __future__ import annotations

import numpy as np
from numpy.testing import assert_allclose

from power_electronics.converters.dc_dc.flyback import FlybackConverter


def test_flyback_instantiation(dc_dc_params):
    conv = FlybackConverter(dc_dc_params)
    assert conv is not None


def test_flyback_simulation(dc_dc_params):
    conv = FlybackConverter(dc_dc_params)
    result = conv.simulate(0.03, 6000)
    for key in ["Vin", "Vout", "IP", "IS", "Q_gate", "Vmag"]:
        assert key in result.signals
        assert len(result.signals[key]) == len(result.time)
        assert np.all(np.isfinite(result.signals[key]))


def test_flyback_theoretical(dc_dc_params):
    conv = FlybackConverter(dc_dc_params)
    result = conv.simulate(0.06, 9000)
    th = conv.get_theoretical_values()["Vout_avg"]
    sim = float(np.mean(result.signals["Vout"][-2500:]))
    assert_allclose(sim, th, rtol=0.02)
    assert conv.get_theoretical_values()["Vout_avg"] > 0
    assert isinstance(conv.get_param_schema(), dict)
