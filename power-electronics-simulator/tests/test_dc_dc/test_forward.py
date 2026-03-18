"""Tests for forward converter."""

from __future__ import annotations

import numpy as np
from numpy.testing import assert_allclose

from power_electronics.converters.dc_dc.forward import ForwardConverter


def test_forward_instantiation(dc_dc_params):
    conv = ForwardConverter(dc_dc_params)
    assert conv is not None


def test_forward_simulation(dc_dc_params):
    conv = ForwardConverter(dc_dc_params)
    result = conv.simulate(0.03, 6000)
    for key in ["Vin", "Vout", "IL"]:
        assert key in result.signals
        assert len(result.signals[key]) == len(result.time)
        assert np.all(np.isfinite(result.signals[key]))
    assert result.converter_name == "forward"


def test_forward_theoretical_includes_turns_ratio(dc_dc_params):
    conv = ForwardConverter(dc_dc_params)
    th = conv.get_theoretical_values()["Vout_avg"]
    vin = float(dc_dc_params["Vin"])
    d = float(dc_dc_params["duty_cycle"])
    n = float(dc_dc_params.get("n", 1.5))
    assert_allclose(th, vin * n * d, rtol=0.01)


def test_forward_schema_has_turns_ratio():
    schema = ForwardConverter.get_param_schema()
    assert "n" in schema


def test_forward_info():
    info = ForwardConverter.get_info()
    assert info.category == "DC-DC"
    assert "Forward" in info.name
