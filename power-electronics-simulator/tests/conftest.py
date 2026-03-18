"""Shared pytest fixtures for converter tests."""

from __future__ import annotations

import pytest


@pytest.fixture
def ac_dc_params() -> dict[str, float]:
    return {
        "Vac_peak": 170.0,
        "frequency": 50.0,
        "R_load": 20.0,
        "L_filter": 1e-3,
        "C_filter": 2e-3,
        "alpha_deg": 30.0,
    }


@pytest.fixture
def dc_dc_params() -> dict[str, float]:
    return {
        "Vin": 48.0,
        "duty_cycle": 0.4,
        "frequency": 20000.0,
        "L": 1e-3,
        "C": 220e-6,
        "R_load": 15.0,
        "R_L": 0.05,
        "n": 2.0,
    }


@pytest.fixture
def dc_ac_params() -> dict[str, float | str]:
    return {
        "Vdc": 300.0,
        "f_output": 50.0,
        "f_carrier": 5000.0,
        "modulation_index": 0.8,
        "R_load": 20.0,
        "L_load": 0.01,
        "C_load": 0.0,
        "control_mode": "SPWM",
    }
