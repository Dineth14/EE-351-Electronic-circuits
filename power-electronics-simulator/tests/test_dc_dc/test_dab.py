"""Tests for dual active bridge converter."""

from __future__ import annotations

import numpy as np

from power_electronics.converters.dc_dc.dual_active_bridge import DualActiveBridgeConverter


def test_dab_instantiation(dc_dc_params):
    params = dict(dc_dc_params)
    params["phase_shift"] = 0.25
    conv = DualActiveBridgeConverter(params)
    assert conv is not None


def test_dab_simulation(dc_dc_params):
    params = dict(dc_dc_params)
    params["phase_shift"] = 0.25
    conv = DualActiveBridgeConverter(params)
    result = conv.simulate(0.03, 6000)
    for key in ["Vin", "Vout", "IL_tank", "Q1", "Q5"]:
        assert key in result.signals
        assert len(result.signals[key]) == len(result.time)
        assert np.all(np.isfinite(result.signals[key]))
    assert result.converter_name == "dual_active_bridge"


def test_dab_metrics(dc_dc_params):
    params = dict(dc_dc_params)
    params["phase_shift"] = 0.25
    conv = DualActiveBridgeConverter(params)
    result = conv.simulate(0.05, 8000)
    assert "Vout_avg" in result.metrics
    assert "efficiency_%" in result.metrics
    assert result.metrics["Vout_avg"] >= 0


def test_dab_schema_has_phase_shift():
    schema = DualActiveBridgeConverter.get_param_schema()
    assert "phase_shift" in schema


def test_dab_theoretical(dc_dc_params):
    params = dict(dc_dc_params)
    params["phase_shift"] = 0.25
    conv = DualActiveBridgeConverter(params)
    th = conv.get_theoretical_values()
    assert "power_transfer_pu" in th
    assert "Vout_avg" in th


def test_dab_info():
    info = DualActiveBridgeConverter.get_info()
    assert info.category == "DC-DC"
    assert "Dual Active Bridge" in info.name
