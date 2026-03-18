"""Tests for boost converter."""

from __future__ import annotations

import numpy as np
from numpy.testing import assert_allclose

from power_electronics.converters.dc_dc.boost import BoostConverter


def test_boost_instantiation(dc_dc_params):
    conv = BoostConverter(dc_dc_params)
    assert conv is not None


def test_boost_simulation(dc_dc_params):
    conv = BoostConverter(dc_dc_params)
    result = conv.simulate(0.03, 6000)
    for key in ["Vin", "Vout", "IL", "IC", "Iout", "Q_gate", "D_current"]:
        assert key in result.signals
        assert len(result.signals[key]) == len(result.time)
        assert np.all(np.isfinite(result.signals[key]))


def test_boost_theoretical(dc_dc_params):
    conv = BoostConverter(dc_dc_params)
    result = conv.simulate(0.06, 9000)
    th = conv.get_theoretical_values()["Vout_avg"]
    sim = float(np.mean(result.signals["Vout"][-2500:]))
    assert_allclose(sim, th, rtol=0.02)
    assert conv.get_theoretical_values()["Vout_avg"] > float(dc_dc_params["Vin"])
    assert isinstance(conv.get_param_schema(), dict)
