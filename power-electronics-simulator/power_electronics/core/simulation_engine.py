"""Numerical simulation helpers used by converter models."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
from scipy.integrate import solve_ivp


def solve_converter_odes(
    ode_func: Callable[[float, np.ndarray], np.ndarray],
    x0: np.ndarray,
    t_span: tuple[float, float],
    n_points: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Solve converter state equations using solve_ivp.

    Parameters
    ----------
    ode_func:
        State derivative function f(t, x).
    x0:
        Initial state vector.
    t_span:
        Start and end times in seconds.
    n_points:
        Number of time samples.
    """
    t_eval = np.linspace(t_span[0], t_span[1], n_points)
    sol = solve_ivp(ode_func, t_span, x0, t_eval=t_eval, method="RK45", max_step=np.inf)
    return sol.t, sol.y


def generate_switch_state(
    t: np.ndarray,
    frequency: float,
    duty_cycle: float,
    dead_time: float = 0.0,
) -> np.ndarray:
    """Generate binary switching state for PWM-like gating."""
    duty = np.clip(duty_cycle, 0.0, 1.0)
    period = 1.0 / max(frequency, 1e-9)
    phase = np.mod(t, period)
    on_time = max(0.0, duty * period - dead_time)
    return (phase < on_time).astype(float)


def generate_scr_pulses(t: np.ndarray, ac_signal: np.ndarray, alpha_deg: float) -> np.ndarray:
    """Generate phase-controlled SCR gating pulses."""
    alpha = np.deg2rad(np.clip(alpha_deg, 0.0, 180.0))
    omega = 2.0 * np.pi
    theta = np.mod(np.arctan2(ac_signal, np.sqrt(np.maximum(1e-12, 1.0 - ac_signal**2))), omega)
    pulse_window = 0.05
    conduction_allowed = theta >= alpha
    narrow_pulse = np.mod(theta - alpha, omega) < pulse_window
    return (conduction_allowed & narrow_pulse).astype(float)


def generate_spwm(
    t: np.ndarray,
    f_carrier: float,
    f_reference: float,
    modulation_index: float,
) -> np.ndarray:
    """Generate sinusoidal PWM comparator output array."""
    m = np.clip(modulation_index, 0.0, 1.0)
    carrier = 2.0 * (np.mod(t * f_carrier, 1.0)) - 1.0
    reference = m * np.sin(2.0 * np.pi * f_reference * t)
    return (reference >= carrier).astype(float)


def detect_conduction_mode(inductor_current: np.ndarray) -> str:
    """Auto-detect conduction mode from inductor current sign."""
    return "DCM" if np.any(inductor_current <= 0.0) else "CCM"
