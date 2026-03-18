"""Tests for Cuk converter."""

from __future__ import annotations

import numpy as np

from power_electronics.converters.dc_dc.cuk import CukConverter


def test_cuk_instantiation(dc_dc_params):
    conv = CukConverter(dc_dc_params)
    assert conv is not None


def test_cuk_simulation(dc_dc_params):
    conv = CukConverter(dc_dc_params)
    result = conv.simulate(0.03, 6000)
    for key in ["Vin", "Vout", "IL", "IL1", "IL2"]:
        assert key in result.signals
        assert len(result.signals[key]) == len(result.time)
        assert np.all(np.isfinite(result.signals[key]))
    assert result.converter_name == "cuk"


def test_cuk_inverted_output(dc_dc_params):
    conv = CukConverter(dc_dc_params)
    result = conv.simulate(0.05, 8000)
    assert float(np.mean(result.signals["Vout"])) <= 0


def test_cuk_info():
    info = CukConverter.get_info()
    assert info.category == "DC-DC"
    assert "Cuk" in info.name
