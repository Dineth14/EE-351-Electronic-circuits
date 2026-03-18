"""Tests for cascaded H-bridge multilevel inverter."""

from __future__ import annotations

import numpy as np

from power_electronics.converters.dc_ac.cascaded_hbridge import CascadedHBridgeInverter


def test_cascaded_instantiation(dc_ac_params):
    params = dict(dc_ac_params)
    params["levels"] = 5.0
    conv = CascadedHBridgeInverter(params)
    assert conv is not None


def test_cascaded_simulation(dc_ac_params):
    params = dict(dc_ac_params)
    params["levels"] = 5.0
    conv = CascadedHBridgeInverter(params)
    result = conv.simulate(0.1, 3000)
    assert "Vout_total" in result.signals
    assert "Iout" in result.signals
    assert result.converter_name == "cascaded_hbridge"
    for name, arr in result.signals.items():
        if isinstance(arr, np.ndarray) and arr.ndim == 1:
            assert len(arr) == len(result.time)
            assert np.all(np.isfinite(arr))
    assert result.metrics["Vout_rms"] > 0


def test_cascaded_schema_has_levels():
    schema = CascadedHBridgeInverter.get_param_schema()
    assert "levels" in schema


def test_cascaded_info():
    info = CascadedHBridgeInverter.get_info()
    assert info.category == "DC-AC"
    assert "Cascaded" in info.name
