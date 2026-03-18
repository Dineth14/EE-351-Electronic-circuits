"""Tests for SEPIC converter."""

from __future__ import annotations

import numpy as np

from power_electronics.converters.dc_dc.sepic import SepicConverter


def test_sepic_instantiation(dc_dc_params):
    conv = SepicConverter(dc_dc_params)
    assert conv is not None


def test_sepic_simulation(dc_dc_params):
    conv = SepicConverter(dc_dc_params)
    result = conv.simulate(0.03, 6000)
    for key in ["Vin", "Vout", "IL", "IL1", "IL2"]:
        assert key in result.signals
        assert len(result.signals[key]) == len(result.time)
        assert np.all(np.isfinite(result.signals[key]))
    assert result.converter_name == "sepic"


def test_sepic_theoretical(dc_dc_params):
    conv = SepicConverter(dc_dc_params)
    th = conv.get_theoretical_values()["Vout_avg"]
    assert th > 0  # non-inverting
    assert isinstance(conv.get_param_schema(), dict)


def test_sepic_info():
    info = SepicConverter.get_info()
    assert info.category == "DC-DC"
    assert "SEPIC" in info.name
