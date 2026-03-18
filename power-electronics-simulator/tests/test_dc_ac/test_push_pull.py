"""Tests for push-pull inverter."""

from __future__ import annotations

import numpy as np

from power_electronics.converters.dc_ac.push_pull import PushPullInverter


def test_push_pull_instantiation(dc_ac_params):
    conv = PushPullInverter(dc_ac_params)
    assert conv is not None


def test_push_pull_simulation(dc_ac_params):
    conv = PushPullInverter(dc_ac_params)
    result = conv.simulate(0.1, 3000)
    assert "Vout" in result.signals
    assert "Iout" in result.signals
    assert result.converter_name == "push_pull"
    for name, arr in result.signals.items():
        if isinstance(arr, np.ndarray) and arr.ndim == 1:
            assert len(arr) == len(result.time)
            assert np.all(np.isfinite(arr))
    assert result.metrics["Vout_rms"] > 0


def test_push_pull_info():
    info = PushPullInverter.get_info()
    assert info.category == "DC-AC"
    assert "Push-Pull" in info.name
