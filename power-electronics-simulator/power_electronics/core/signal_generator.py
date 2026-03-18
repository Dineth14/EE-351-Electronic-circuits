"""Convenience wrappers for switching and modulation signal generation."""

from __future__ import annotations

import numpy as np

from power_electronics.core.simulation_engine import (
    generate_scr_pulses,
    generate_spwm,
    generate_switch_state,
)


def square_wave(t: np.ndarray, frequency: float, duty_cycle: float = 0.5) -> np.ndarray:
    """Generate a square-wave gating signal."""
    return generate_switch_state(t=t, frequency=frequency, duty_cycle=duty_cycle)


def firing_pulses(t: np.ndarray, ac_signal: np.ndarray, alpha_deg: float) -> np.ndarray:
    """Generate SCR firing pulses."""
    return generate_scr_pulses(t=t, ac_signal=ac_signal, alpha_deg=alpha_deg)


def spwm(t: np.ndarray, f_carrier: float, f_reference: float, modulation_index: float) -> np.ndarray:
    """Generate SPWM duty array from carrier and sinusoidal references."""
    return generate_spwm(t=t, f_carrier=f_carrier, f_reference=f_reference, modulation_index=modulation_index)
