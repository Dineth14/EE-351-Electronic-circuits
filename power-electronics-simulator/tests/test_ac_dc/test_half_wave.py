"""Tests for half-wave rectifier."""

from __future__ import annotations

import numpy as np
from numpy.testing import assert_allclose

from power_electronics.converters.ac_dc.half_wave import HalfWaveRectifier


def test_half_wave_instantiation(ac_dc_params):
    conv = HalfWaveRectifier(ac_dc_params)
    assert conv is not None


def test_half_wave_simulation_structure(ac_dc_params):
    conv = HalfWaveRectifier(ac_dc_params)
    result = conv.simulate(0.2, 5000)
    assert result.converter_name == "half_wave"
    for key in ["Vac", "Vout_raw", "Vout_filtered", "ID", "IL", "IC"]:
        assert key in result.signals
    assert "Vdc_avg" in result.metrics
    for arr in result.signals.values():
        if isinstance(arr, np.ndarray):
            if arr.ndim == 1:
                assert len(arr) == len(result.time)
                assert np.all(np.isfinite(arr))


def test_half_wave_theoretical_close(ac_dc_params):
    conv = HalfWaveRectifier(ac_dc_params)
    result = conv.simulate(0.3, 6000)
    th = conv.get_theoretical_values()["Vdc_avg"]
    sim = float(np.mean(result.signals["Vdc_raw"]))
    assert_allclose(sim, th, rtol=0.02)
    assert conv.get_param_schema()["Vac_peak"]["type"] == "float"
    assert conv.get_theoretical_values()["Vdc_avg"] > 0
