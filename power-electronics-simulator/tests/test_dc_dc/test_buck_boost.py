"""Tests for buck-boost converter."""

from __future__ import annotations

import numpy as np
from numpy.testing import assert_allclose

from power_electronics.converters.dc_dc.buck_boost import BuckBoostConverter


def test_buck_boost_instantiation(dc_dc_params):
    conv = BuckBoostConverter(dc_dc_params)
    assert conv is not None


def test_buck_boost_simulation(dc_dc_params):
    conv = BuckBoostConverter(dc_dc_params)
    result = conv.simulate(0.03, 6000)
    for key in ["Vin", "Vout", "IL", "IC", "Iout"]:
        assert key in result.signals
        assert len(result.signals[key]) == len(result.time)
        assert np.all(np.isfinite(result.signals[key]))


def test_buck_boost_inverted_output(dc_dc_params):
    conv = BuckBoostConverter(dc_dc_params)
    result = conv.simulate(0.05, 8000)
    # Buck-boost output is inverted (negative)
    assert float(np.mean(result.signals["Vout"])) <= 0


def test_buck_boost_theoretical(dc_dc_params):
    conv = BuckBoostConverter(dc_dc_params)
    th = conv.get_theoretical_values()["Vout_avg"]
    assert th < 0  # inverted
    assert isinstance(conv.get_param_schema(), dict)
    assert conv.get_info().category == "DC-DC"
