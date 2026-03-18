from __future__ import annotations

import numpy as np

try:
    from .utils import electrical_angle, multi_phase_sine, sine_wave, waveform_metrics
except ImportError:  # pragma: no cover - direct script execution fallback
    from utils import electrical_angle, multi_phase_sine, sine_wave, waveform_metrics


def single_phase_half_wave_theory(source_peak: float, alpha: float = 0.0, controlled: bool = False) -> dict[str, float]:
    """Theoretical average and RMS output for a single-phase half-wave R load rectifier."""
    vm = float(source_peak)
    if controlled:
        alpha = float(np.clip(alpha, 0.0, np.pi))
    else:
        alpha = 0.0

    vdc = vm * (1.0 + np.cos(alpha)) / (2.0 * np.pi)
    vrms = vm * np.sqrt((np.pi - alpha) / (4.0 * np.pi) + np.sin(2.0 * alpha) / (8.0 * np.pi))
    return {"vdc": float(vdc), "vrms": float(vrms)}


def single_phase_full_bridge_theory(
    source_peak: float,
    alpha: float = 0.0,
    controlled: bool = False,
    continuous_current: bool = False,
) -> dict[str, float]:
    """Theoretical average and RMS output for single-phase bridge rectifiers."""
    vm = float(source_peak)
    if not controlled:
        return {"vdc": float(2.0 * vm / np.pi), "vrms": float(vm / np.sqrt(2.0))}

    alpha = float(np.clip(alpha, 0.0, np.pi))
    if continuous_current:
        return {"vdc": float(2.0 * vm * np.cos(alpha) / np.pi), "vrms": float(vm / np.sqrt(2.0))}

    vdc = vm * (1.0 + np.cos(alpha)) / np.pi
    vrms = vm * np.sqrt((np.pi - alpha) / (2.0 * np.pi) + np.sin(2.0 * alpha) / (4.0 * np.pi))
    return {"vdc": float(vdc), "vrms": float(vrms)}


def three_phase_bridge_theory(phase_peak: float, alpha: float = 0.0, controlled: bool = False) -> dict[str, float]:
    """Approximate six-pulse bridge average output formula from line-line peak voltage."""
    vll_peak = float(np.sqrt(3.0) * phase_peak)
    if controlled:
        alpha = float(np.clip(alpha, 0.0, np.pi / 2.0))
        vdc = 3.0 * vll_peak * np.cos(alpha) / np.pi
    else:
        vdc = 3.0 * vll_peak / np.pi
    return {"vdc": float(vdc)}


def _controlled_sign(theta: np.ndarray, alpha: float) -> np.ndarray:
    interval = np.floor(np.mod(theta - alpha, 2.0 * np.pi) / np.pi).astype(int)
    return np.where(interval % 2 == 0, 1.0, -1.0)


def _gating_window(theta: np.ndarray, alpha: float) -> np.ndarray:
    return np.mod(theta, np.pi) >= alpha


def single_phase_half_wave_rectifier(
    time: np.ndarray,
    source_peak: float = 325.0,
    frequency: float = 50.0,
    alpha: float = 0.0,
    controlled: bool = False,
) -> dict[str, np.ndarray | float | dict[str, float]]:
    """Single-phase half-wave diode or SCR rectifier with an R load."""
    source_voltage = sine_wave(time, amplitude=source_peak, frequency=frequency)
    theta = electrical_angle(time, frequency)

    if controlled:
        alpha = float(np.clip(alpha, 0.0, np.pi))
        conducting = (theta >= alpha) & (theta <= np.pi)
    else:
        conducting = source_voltage >= 0.0

    output_voltage = np.where(conducting, source_voltage, 0.0)
    theory = single_phase_half_wave_theory(source_peak=source_peak, alpha=alpha, controlled=controlled)
    return {
        "time": np.asarray(time, dtype=float),
        "angle": theta,
        "source_voltage": source_voltage,
        "output_voltage": output_voltage,
        "conduction": conducting.astype(float),
        "theory": theory,
        "metrics": waveform_metrics(output_voltage),
    }


def single_phase_full_bridge_rectifier(
    time: np.ndarray,
    source_peak: float = 325.0,
    frequency: float = 50.0,
    alpha: float = 0.0,
    controlled: bool = False,
    continuous_current: bool = False,
) -> dict[str, np.ndarray | float | dict[str, float]]:
    """Single-phase bridge rectifier for diode or fully controlled SCR operation."""
    source_voltage = sine_wave(time, amplitude=source_peak, frequency=frequency)
    theta = electrical_angle(time, frequency)

    if not controlled:
        output_voltage = np.abs(source_voltage)
        conduction = np.sign(source_voltage)
    elif continuous_current:
        sign_function = _controlled_sign(theta, float(np.clip(alpha, 0.0, np.pi)))
        output_voltage = sign_function * source_voltage
        conduction = sign_function
    else:
        alpha = float(np.clip(alpha, 0.0, np.pi))
        conducting = _gating_window(theta, alpha)
        output_voltage = np.where(conducting, np.abs(source_voltage), 0.0)
        conduction = conducting.astype(float)

    theory = single_phase_full_bridge_theory(
        source_peak=source_peak,
        alpha=alpha,
        controlled=controlled,
        continuous_current=continuous_current,
    )

    return {
        "time": np.asarray(time, dtype=float),
        "angle": theta,
        "source_voltage": source_voltage,
        "output_voltage": output_voltage,
        "conduction": conduction,
        "theory": theory,
        "metrics": waveform_metrics(output_voltage),
    }


def three_phase_half_wave_rectifier(
    time: np.ndarray,
    phase_peak: float = 325.0,
    frequency: float = 50.0,
    alpha: float = 0.0,
    controlled: bool = False,
) -> dict[str, np.ndarray | float | dict[str, float]]:
    """Three-phase half-wave rectifier using a neutral return path."""
    phase_voltages = multi_phase_sine(time, amplitude=phase_peak, frequency=frequency)
    theta = electrical_angle(time, frequency)

    if controlled:
        delayed_phases = multi_phase_sine(
            time,
            amplitude=phase_peak,
            frequency=frequency,
            phase_offsets=(-alpha, -2.0 * np.pi / 3.0 - alpha, 2.0 * np.pi / 3.0 - alpha),
        )
        conducting_phase = np.argmax(delayed_phases, axis=0)
        output_voltage = phase_voltages[conducting_phase, np.arange(phase_voltages.shape[1])]
    else:
        stacked = np.vstack((phase_voltages, np.zeros(phase_voltages.shape[1])))
        conducting_phase = np.argmax(stacked, axis=0)
        output_voltage = np.max(stacked, axis=0)

    return {
        "time": np.asarray(time, dtype=float),
        "angle": theta,
        "phase_voltages": phase_voltages,
        "output_voltage": output_voltage,
        "conducting_phase": conducting_phase,
        "theory": {"vdc": float(3.0 * np.sqrt(3.0) * phase_peak / (2.0 * np.pi))},
        "metrics": waveform_metrics(output_voltage),
    }


def three_phase_bridge_rectifier(
    time: np.ndarray,
    phase_peak: float = 325.0,
    frequency: float = 50.0,
    alpha: float = 0.0,
    controlled: bool = False,
) -> dict[str, np.ndarray | float | dict[str, float]]:
    """Six-pulse three-phase bridge rectifier."""
    phase_voltages = multi_phase_sine(time, amplitude=phase_peak, frequency=frequency)
    theta = electrical_angle(time, frequency)
    line_voltages = {
        "v_ab": phase_voltages[0] - phase_voltages[1],
        "v_bc": phase_voltages[1] - phase_voltages[2],
        "v_ca": phase_voltages[2] - phase_voltages[0],
    }

    if controlled:
        delayed_phases = multi_phase_sine(
            time,
            amplitude=phase_peak,
            frequency=frequency,
            phase_offsets=(-alpha, -2.0 * np.pi / 3.0 - alpha, 2.0 * np.pi / 3.0 - alpha),
        )
    else:
        delayed_phases = phase_voltages

    top_phase = np.argmax(delayed_phases, axis=0)
    bottom_phase = np.argmin(delayed_phases, axis=0)
    output_voltage = phase_voltages[top_phase, np.arange(phase_voltages.shape[1])] - phase_voltages[bottom_phase, np.arange(phase_voltages.shape[1])]
    theory = three_phase_bridge_theory(phase_peak=phase_peak, alpha=alpha, controlled=controlled)

    return {
        "time": np.asarray(time, dtype=float),
        "angle": theta,
        "phase_voltages": phase_voltages,
        "line_voltages": line_voltages,
        "output_voltage": output_voltage,
        "top_phase": top_phase,
        "bottom_phase": bottom_phase,
        "theory": theory,
        "metrics": waveform_metrics(output_voltage),
    }
