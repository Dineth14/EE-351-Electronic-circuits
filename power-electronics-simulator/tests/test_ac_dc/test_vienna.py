"""Tests for Vienna rectifier."""

from __future__ import annotations

import numpy as np

from power_electronics.converters.ac_dc.vienna_rectifier import ViennaRectifier


def test_vienna_instantiation(ac_dc_params):
    conv = ViennaRectifier(ac_dc_params)
    assert conv is not None


def test_vienna_simulation(ac_dc_params):
    conv = ViennaRectifier(ac_dc_params)
    result = conv.simulate(0.2, 4000)
    assert "Vdc_filtered" in result.signals
    assert "switch_state" in result.signals
    assert result.converter_name == "vienna_rectifier"
    for name, arr in result.signals.items():
        if isinstance(arr, np.ndarray) and arr.ndim == 1:
            assert len(arr) == len(result.time)
            assert np.all(np.isfinite(arr))
    assert result.metrics["Vdc_avg"] > 0


def test_vienna_high_power_factor(ac_dc_params):
    conv = ViennaRectifier(ac_dc_params)
    result = conv.simulate(0.2, 4000)
    assert result.metrics["power_factor"] >= 0.95


def test_vienna_low_thd(ac_dc_params):
    conv = ViennaRectifier(ac_dc_params)
    result = conv.simulate(0.2, 4000)
    assert result.metrics["THD_%"] <= 5.0


def test_vienna_info(ac_dc_params):
    assert ViennaRectifier.get_info().name == "Vienna Rectifier"
    assert ViennaRectifier.get_info().category == "AC-DC"
