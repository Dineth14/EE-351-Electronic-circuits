"""Tests for full-wave center-tap rectifier."""

from __future__ import annotations

import numpy as np
from numpy.testing import assert_allclose

from power_electronics.converters.ac_dc.full_wave_centertap import FullWaveCenterTapRectifier


def test_centertap_instantiation(ac_dc_params):
    conv = FullWaveCenterTapRectifier(ac_dc_params)
    assert conv is not None


def test_centertap_simulation_structure(ac_dc_params):
    conv = FullWaveCenterTapRectifier(ac_dc_params)
    result = conv.simulate(0.2, 4000)
    for key in ["Vac", "Vdc_raw", "Vdc_filtered", "Iload"]:
        assert key in result.signals
    for name, arr in result.signals.items():
        if isinstance(arr, np.ndarray) and arr.ndim == 1:
            assert len(arr) == len(result.time)
            assert np.all(np.isfinite(arr))
    assert result.metrics["Vdc_avg"] > 0


def test_centertap_theoretical_close(ac_dc_params):
    conv = FullWaveCenterTapRectifier(ac_dc_params)
    result = conv.simulate(0.3, 6000)
    th = conv.get_theoretical_values()["Vdc_avg"]
    sim = float(np.mean(result.signals["Vdc_raw"]))
    assert_allclose(sim, th, rtol=0.05)
    assert isinstance(conv.get_param_schema(), dict)
    assert conv.get_info().category == "AC-DC"
