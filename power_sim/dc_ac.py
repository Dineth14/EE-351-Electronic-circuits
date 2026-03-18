from __future__ import annotations

import numpy as np

try:
    from .utils import comparator, electrical_angle, frequency_ratio, waveform_metrics, triangle_carrier
except ImportError:  # pragma: no cover - direct script execution fallback
    from utils import comparator, electrical_angle, frequency_ratio, waveform_metrics, triangle_carrier


def single_phase_square_theory(dc_bus: float, topology: str = "full_bridge") -> dict[str, float]:
    """Fundamental component estimates for single-phase square-wave inverters."""
    topology_key = topology.lower()
    if topology_key == "half_bridge":
        v1_peak = 2.0 * (dc_bus / 2.0) / np.pi
    elif topology_key == "full_bridge":
        v1_peak = 4.0 * (dc_bus / 2.0) / np.pi
    else:
        raise ValueError("topology must be 'half_bridge' or 'full_bridge'.")
    return {"v1_peak": float(v1_peak), "v1_rms": float(v1_peak / np.sqrt(2.0))}


def single_phase_spwm_theory(dc_bus: float, modulation_index: float) -> dict[str, float]:
    """Linear modulation fundamental estimate for full-bridge SPWM."""
    m_a = float(np.clip(modulation_index, 0.0, 1.0))
    v1_peak = m_a * dc_bus
    return {"v1_peak": float(v1_peak), "v1_rms": float(v1_peak / np.sqrt(2.0)), "m_a_linear": m_a}


def _phase_voltage_set(pole_voltages: np.ndarray) -> np.ndarray:
    common_mode = np.mean(pole_voltages, axis=0)
    return pole_voltages - common_mode


def single_phase_half_bridge_square(
    time: np.ndarray,
    dc_bus: float = 200.0,
    output_frequency: float = 50.0,
) -> dict[str, np.ndarray | dict[str, float]]:
    theta = electrical_angle(time, output_frequency)
    upper_switch = np.sin(theta) >= 0.0
    output_voltage = np.where(upper_switch, dc_bus / 2.0, -dc_bus / 2.0)
    theory = single_phase_square_theory(dc_bus=dc_bus, topology="half_bridge")

    return {
        "time": np.asarray(time, dtype=float),
        "angle": theta,
        "upper_switch": upper_switch.astype(float),
        "output_voltage": output_voltage,
        "theory": theory,
        "metrics": waveform_metrics(output_voltage),
    }


def single_phase_full_bridge_square(
    time: np.ndarray,
    dc_bus: float = 200.0,
    output_frequency: float = 50.0,
) -> dict[str, np.ndarray | dict[str, float]]:
    theta = electrical_angle(time, output_frequency)
    leg_a_high = np.sin(theta) >= 0.0
    leg_b_high = ~leg_a_high
    pole_a = np.where(leg_a_high, dc_bus / 2.0, -dc_bus / 2.0)
    pole_b = np.where(leg_b_high, dc_bus / 2.0, -dc_bus / 2.0)
    output_voltage = pole_a - pole_b
    theory = single_phase_square_theory(dc_bus=dc_bus, topology="full_bridge")

    return {
        "time": np.asarray(time, dtype=float),
        "angle": theta,
        "pole_a": pole_a,
        "pole_b": pole_b,
        "output_voltage": output_voltage,
        "theory": theory,
        "metrics": waveform_metrics(output_voltage),
    }


def single_phase_bipolar_spwm(
    time: np.ndarray,
    dc_bus: float = 200.0,
    output_frequency: float = 50.0,
    carrier_frequency: float = 5000.0,
    modulation_index: float = 0.9,
) -> dict[str, np.ndarray | float | dict[str, float]]:
    theta = electrical_angle(time, output_frequency)
    reference = modulation_index * np.sin(theta)
    carrier = triangle_carrier(time, frequency=carrier_frequency, amplitude=1.0)
    switching_function = comparator(reference, carrier, high_level=1.0, low_level=0.0)
    output_voltage = np.where(switching_function > 0.5, dc_bus, -dc_bus)
    theory = single_phase_spwm_theory(dc_bus=dc_bus, modulation_index=modulation_index)

    return {
        "time": np.asarray(time, dtype=float),
        "angle": theta,
        "reference": reference,
        "carrier": carrier,
        "switching_function": switching_function,
        "output_voltage": output_voltage,
        "m_a": float(modulation_index),
        "m_f": frequency_ratio(carrier_frequency, output_frequency),
        "theory": theory,
        "metrics": waveform_metrics(output_voltage),
    }


def single_phase_unipolar_spwm(
    time: np.ndarray,
    dc_bus: float = 200.0,
    output_frequency: float = 50.0,
    carrier_frequency: float = 5000.0,
    modulation_index: float = 0.9,
) -> dict[str, np.ndarray | float | dict[str, float]]:
    theta = electrical_angle(time, output_frequency)
    reference_a = modulation_index * np.sin(theta)
    reference_b = -reference_a
    carrier = triangle_carrier(time, frequency=carrier_frequency, amplitude=1.0)
    leg_a_high = comparator(reference_a, carrier, high_level=1.0, low_level=0.0)
    leg_b_high = comparator(reference_b, carrier, high_level=1.0, low_level=0.0)
    pole_a = np.where(leg_a_high > 0.5, dc_bus / 2.0, -dc_bus / 2.0)
    pole_b = np.where(leg_b_high > 0.5, dc_bus / 2.0, -dc_bus / 2.0)
    output_voltage = pole_a - pole_b
    theory = single_phase_spwm_theory(dc_bus=dc_bus, modulation_index=modulation_index)

    return {
        "time": np.asarray(time, dtype=float),
        "angle": theta,
        "reference_a": reference_a,
        "reference_b": reference_b,
        "carrier": carrier,
        "pole_a": pole_a,
        "pole_b": pole_b,
        "output_voltage": output_voltage,
        "m_a": float(modulation_index),
        "m_f": frequency_ratio(carrier_frequency, output_frequency),
        "theory": theory,
        "metrics": waveform_metrics(output_voltage),
    }


def _phase_state_180(theta: np.ndarray, phase_shift: float) -> np.ndarray:
    return np.where(np.sin(theta + phase_shift) >= 0.0, 1.0, -1.0)


def _phase_state_120(theta: np.ndarray, phase_shift: float) -> np.ndarray:
    shifted = np.mod(theta + phase_shift, 2.0 * np.pi)
    state = np.zeros_like(shifted)
    state[(shifted >= np.pi / 6.0) & (shifted < 5.0 * np.pi / 6.0)] = 1.0
    state[(shifted >= 7.0 * np.pi / 6.0) & (shifted < 11.0 * np.pi / 6.0)] = -1.0
    return state


def three_phase_six_step(
    time: np.ndarray,
    dc_bus: float = 400.0,
    output_frequency: float = 50.0,
    conduction_mode: int = 180,
) -> dict[str, np.ndarray | dict[str, float]]:
    """Three-phase inverter in 180 or 120 degree conduction mode."""
    theta = electrical_angle(time, output_frequency)
    phase_shifts = (0.0, -2.0 * np.pi / 3.0, 2.0 * np.pi / 3.0)

    if conduction_mode == 180:
        states = np.vstack([_phase_state_180(theta, shift) for shift in phase_shifts])
    elif conduction_mode == 120:
        states = np.vstack([_phase_state_120(theta, shift) for shift in phase_shifts])
    else:
        raise ValueError("conduction_mode must be either 120 or 180 degrees.")

    pole_voltages = 0.5 * dc_bus * states
    phase_voltages = _phase_voltage_set(pole_voltages)
    line_voltages = {
        "v_ab": pole_voltages[0] - pole_voltages[1],
        "v_bc": pole_voltages[1] - pole_voltages[2],
        "v_ca": pole_voltages[2] - pole_voltages[0],
    }
    vll1_rms = (np.sqrt(6.0) / np.pi) * dc_bus

    return {
        "time": np.asarray(time, dtype=float),
        "angle": theta,
        "states": states,
        "pole_voltages": pole_voltages,
        "phase_voltages": phase_voltages,
        "line_voltages": line_voltages,
        "conduction_mode": int(conduction_mode),
        "theory": {"vll1_rms": float(vll1_rms)},
        "metrics": waveform_metrics(line_voltages["v_ab"]),
    }
