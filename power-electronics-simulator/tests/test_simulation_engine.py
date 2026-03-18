"""Tests for simulation engine helper functions."""

from __future__ import annotations

import numpy as np
from numpy.testing import assert_allclose

from power_electronics.core.simulation_engine import (
    detect_conduction_mode,
    generate_scr_pulses,
    generate_spwm,
    generate_switch_state,
    solve_converter_odes,
)


class TestSolveODE:
    def test_basic_decay(self):
        """Solve dx/dt = -x, x(0) = 1 → x(t) = e^(-t)."""
        def ode(t, x):
            return -x
        t, y = solve_converter_odes(ode, np.array([1.0]), (0.0, 5.0), 500)
        assert len(t) == 500
        assert y.shape == (1, 500)
        assert_allclose(y[0, -1], np.exp(-5.0), rtol=0.05)

    def test_output_dimensions(self):
        def ode(t, x):
            return np.array([-x[0], x[0] - x[1]])
        t, y = solve_converter_odes(ode, np.array([1.0, 0.0]), (0.0, 1.0), 200)
        assert t.shape == (200,)
        assert y.shape == (2, 200)


class TestSwitchState:
    def test_duty_cycle_ratio(self):
        t = np.linspace(0.0, 0.01, 10000)  # 10ms, 100Hz
        q = generate_switch_state(t, 100.0, 0.6)
        actual_duty = np.mean(q)
        assert_allclose(actual_duty, 0.6, atol=0.05)

    def test_binary_output(self):
        t = np.linspace(0.0, 0.001, 1000)
        q = generate_switch_state(t, 10000.0, 0.5)
        assert set(np.unique(q)).issubset({0.0, 1.0})

    def test_clamp_duty_cycle(self):
        t = np.linspace(0.0, 0.001, 100)
        q_high = generate_switch_state(t, 1000.0, 1.5)
        assert np.all(q_high == 1.0)
        q_low = generate_switch_state(t, 1000.0, -0.5)
        assert np.all(q_low == 0.0)


class TestSCRPulses:
    def test_produces_binary(self):
        t = np.linspace(0.0, 0.04, 2000)
        ac = np.sin(2.0 * np.pi * 50.0 * t)
        pulses = generate_scr_pulses(t, ac, 30.0)
        assert set(np.unique(pulses)).issubset({0.0, 1.0})


class TestSPWM:
    def test_produces_binary(self):
        t = np.linspace(0.0, 0.02, 5000)
        q = generate_spwm(t, 5000.0, 50.0, 0.8)
        assert set(np.unique(q)).issubset({0.0, 1.0})

    def test_modulation_index_clamp(self):
        t = np.linspace(0.0, 0.02, 1000)
        q = generate_spwm(t, 5000.0, 50.0, 1.5)
        assert set(np.unique(q)).issubset({0.0, 1.0})


class TestConductionMode:
    def test_ccm(self):
        il = np.array([1.0, 2.0, 1.5, 2.5])
        assert detect_conduction_mode(il) == "CCM"

    def test_dcm(self):
        il = np.array([1.0, 0.0, 2.0, 0.5])
        assert detect_conduction_mode(il) == "DCM"
