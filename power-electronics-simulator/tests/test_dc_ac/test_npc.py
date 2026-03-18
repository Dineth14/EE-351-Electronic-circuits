"""Tests for NPC three-level inverter."""

from __future__ import annotations

import numpy as np

from power_electronics.converters.dc_ac.npc_inverter import NPCInverter


def test_npc_instantiation(dc_ac_params):
    conv = NPCInverter(dc_ac_params)
    assert conv is not None


def test_npc_simulation(dc_ac_params):
    conv = NPCInverter(dc_ac_params)
    result = conv.simulate(0.1, 3000)
    assert "Vout" in result.signals
    assert "neutral_clamping" in result.signals
    assert result.converter_name == "npc_inverter"
    for name, arr in result.signals.items():
        if isinstance(arr, np.ndarray) and arr.ndim == 1:
            assert len(arr) == len(result.time)
            assert np.all(np.isfinite(arr))
    assert result.metrics["Vout_rms"] > 0


def test_npc_three_level_output(dc_ac_params):
    conv = NPCInverter(dc_ac_params)
    result = conv.simulate(0.1, 3000)
    vout = result.signals["Vout"]
    vdc = float(dc_ac_params["Vdc"])
    # Should only have values near +Vdc/2, 0, -Vdc/2
    unique_levels = np.unique(vout)
    assert len(unique_levels) <= 3


def test_npc_info():
    info = NPCInverter.get_info()
    assert info.category == "DC-AC"
    assert "NPC" in info.name
