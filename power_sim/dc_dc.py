from __future__ import annotations

import numpy as np

try:
    from .utils import waveform_metrics
except ImportError:  # pragma: no cover - direct script execution fallback
    from utils import waveform_metrics


def buck_theory(input_voltage: float, duty_cycle: float, mode: str, k_value: float) -> dict[str, float | str]:
    duty = float(np.clip(duty_cycle, 0.0, 1.0))
    mode_key = mode.upper()
    if mode_key == "CCM":
        ratio = duty
        formula = "M = D"
    elif mode_key == "DCM":
        ratio = 2.0 / (1.0 + np.sqrt(1.0 + 4.0 * k_value / max(duty**2, 1e-12)))
        formula = "M = 2 / (1 + sqrt(1 + 4K/D^2))"
    else:
        raise ValueError("mode must be 'CCM' or 'DCM'.")
    return {"mode": mode_key, "formula": formula, "M": float(ratio), "Vout": float(ratio * input_voltage)}


def boost_theory(input_voltage: float, duty_cycle: float, mode: str, k_value: float) -> dict[str, float | str]:
    duty = float(np.clip(duty_cycle, 0.0, 0.999))
    mode_key = mode.upper()
    if mode_key == "CCM":
        ratio = 1.0 / (1.0 - duty)
        formula = "M = 1/(1-D)"
    elif mode_key == "DCM":
        ratio = 0.5 * (1.0 + np.sqrt(1.0 + 4.0 * duty**2 / max(k_value, 1e-12)))
        formula = "M = 0.5*(1 + sqrt(1 + 4D^2/K))"
    else:
        raise ValueError("mode must be 'CCM' or 'DCM'.")
    return {"mode": mode_key, "formula": formula, "M": float(ratio), "Vout": float(ratio * input_voltage)}


def buck_boost_theory(input_voltage: float, duty_cycle: float, mode: str, k_value: float) -> dict[str, float | str]:
    duty = float(np.clip(duty_cycle, 0.0, 0.999))
    mode_key = mode.upper()
    if mode_key == "CCM":
        ratio = -(duty / (1.0 - duty))
        formula = "M = -D/(1-D)"
    elif mode_key == "DCM":
        ratio = -duty / np.sqrt(max(k_value, 1e-12))
        formula = "M = -D/sqrt(K)"
    else:
        raise ValueError("mode must be 'CCM' or 'DCM'.")
    return {"mode": mode_key, "formula": formula, "M": float(ratio), "Vout": float(ratio * input_voltage)}


def _switch_phase(time: np.ndarray, switching_frequency: float) -> np.ndarray:
    return np.mod(np.asarray(time, dtype=float) * switching_frequency, 1.0)


def _current_ripple_profile(
    phase: np.ndarray,
    duty: float,
    discharge_fraction: float,
    i_min: float,
    i_peak: float,
) -> np.ndarray:
    current = np.zeros_like(phase)
    on_region = phase < duty
    discharge_end = duty + discharge_fraction
    discharge_region = (phase >= duty) & (phase < discharge_end)

    if duty > 0.0:
        current[on_region] = i_min + (i_peak - i_min) * phase[on_region] / duty

    if discharge_fraction > 0.0:
        current[discharge_region] = i_peak * (1.0 - (phase[discharge_region] - duty) / discharge_fraction)

    return current


def _capacitor_voltage_from_current(time: np.ndarray, capacitor_current: np.ndarray, capacitance: float | None) -> np.ndarray:
    if capacitance is None or capacitance <= 0.0 or len(time) < 2:
        return np.zeros_like(capacitor_current)

    dt = np.diff(np.asarray(time, dtype=float), prepend=float(time[0]))
    ripple = np.cumsum((capacitor_current - np.mean(capacitor_current)) * dt / capacitance)
    return ripple - np.mean(ripple)


def buck_converter(
    time: np.ndarray,
    input_voltage: float,
    duty_cycle: float,
    switching_frequency: float,
    resistance: float,
    inductance: float,
    capacitance: float | None = None,
    mode: str = "CCM",
) -> dict[str, np.ndarray | float | dict[str, float]]:
    """Ideal buck converter waveforms for CCM or DCM."""
    duty = float(np.clip(duty_cycle, 0.0, 1.0))
    time = np.asarray(time, dtype=float)
    phase = _switch_phase(time, switching_frequency)
    ts = 1.0 / switching_frequency
    mode = mode.upper()
    k_value = 2.0 * inductance * switching_frequency / resistance

    if mode == "CCM":
        output_average = duty * input_voltage
        load_current = output_average / resistance
        delta_i = (input_voltage - output_average) * duty * ts / inductance
        i_min = load_current - 0.5 * delta_i
        i_peak = load_current + 0.5 * delta_i
        discharge_fraction = max(1.0 - duty, 1e-12)
        inductor_current = _current_ripple_profile(phase, duty, discharge_fraction, i_min, i_peak)
        inductor_voltage = np.where(phase < duty, input_voltage - output_average, -output_average)
        diode_current = np.where(phase >= duty, inductor_current, 0.0)
    elif mode == "DCM":
        output_ratio = 2.0 / (1.0 + np.sqrt(1.0 + 4.0 * k_value / max(duty**2, 1e-12)))
        output_average = output_ratio * input_voltage
        i_peak = (input_voltage - output_average) * duty * ts / inductance
        discharge_fraction = duty * (1.0 - output_ratio) / max(output_ratio, 1e-12)
        inductor_current = _current_ripple_profile(phase, duty, discharge_fraction, 0.0, i_peak)
        inductor_voltage = np.where(
            phase < duty,
            input_voltage - output_average,
            np.where(phase < duty + discharge_fraction, -output_average, 0.0),
        )
        diode_current = np.where((phase >= duty) & (phase < duty + discharge_fraction), inductor_current, 0.0)
        delta_i = i_peak
        load_current = output_average / resistance
    else:
        raise ValueError("mode must be 'CCM' or 'DCM'.")

    switch_current = np.where(phase < duty, inductor_current, 0.0)
    capacitor_current = inductor_current - load_current
    capacitor_voltage = _capacitor_voltage_from_current(time, capacitor_current, capacitance)
    output_voltage = output_average + capacitor_voltage
    theory = buck_theory(input_voltage=input_voltage, duty_cycle=duty, mode=mode, k_value=k_value)

    return {
        "time": time,
        "switch": (phase < duty).astype(float),
        "inductor_current": inductor_current,
        "switch_current": switch_current,
        "diode_current": diode_current,
        "inductor_voltage": inductor_voltage,
        "output_voltage": output_voltage,
        "load_current": np.full_like(time, load_current),
        "capacitor_current": capacitor_current,
        "mode": mode,
        "theory": theory,
        "average_output_voltage": float(output_average),
        "current_ripple_pp": float(delta_i),
        "boundary_inductance": float((1.0 - duty) * resistance / (2.0 * switching_frequency)),
        "metrics": waveform_metrics(output_voltage),
    }


def boost_converter(
    time: np.ndarray,
    input_voltage: float,
    duty_cycle: float,
    switching_frequency: float,
    resistance: float,
    inductance: float,
    capacitance: float | None = None,
    mode: str = "CCM",
) -> dict[str, np.ndarray | float | dict[str, float]]:
    """Ideal boost converter waveforms for CCM or DCM."""
    duty = float(np.clip(duty_cycle, 0.0, 0.999))
    time = np.asarray(time, dtype=float)
    phase = _switch_phase(time, switching_frequency)
    ts = 1.0 / switching_frequency
    mode = mode.upper()
    k_value = 2.0 * inductance * switching_frequency / resistance

    if mode == "CCM":
        output_average = input_voltage / (1.0 - duty)
        load_current = output_average / resistance
        average_inductor_current = load_current / (1.0 - duty)
        delta_i = input_voltage * duty * ts / inductance
        i_min = average_inductor_current - 0.5 * delta_i
        i_peak = average_inductor_current + 0.5 * delta_i
        discharge_fraction = max(1.0 - duty, 1e-12)
        inductor_current = _current_ripple_profile(phase, duty, discharge_fraction, i_min, i_peak)
        diode_current = np.where(phase >= duty, inductor_current, 0.0)
        inductor_voltage = np.where(phase < duty, input_voltage, input_voltage - output_average)
    elif mode == "DCM":
        output_ratio = 0.5 * (1.0 + np.sqrt(1.0 + 4.0 * duty**2 / max(k_value, 1e-12)))
        output_average = output_ratio * input_voltage
        load_current = output_average / resistance
        i_peak = input_voltage * duty * ts / inductance
        discharge_fraction = duty / max(output_ratio - 1.0, 1e-12)
        inductor_current = _current_ripple_profile(phase, duty, discharge_fraction, 0.0, i_peak)
        diode_current = np.where((phase >= duty) & (phase < duty + discharge_fraction), inductor_current, 0.0)
        inductor_voltage = np.where(
            phase < duty,
            input_voltage,
            np.where(phase < duty + discharge_fraction, input_voltage - output_average, 0.0),
        )
        delta_i = i_peak
    else:
        raise ValueError("mode must be 'CCM' or 'DCM'.")

    switch_current = np.where(phase < duty, inductor_current, 0.0)
    capacitor_current = diode_current - load_current
    capacitor_voltage = _capacitor_voltage_from_current(time, capacitor_current, capacitance)
    output_voltage = output_average + capacitor_voltage
    theory = boost_theory(input_voltage=input_voltage, duty_cycle=duty, mode=mode, k_value=k_value)

    return {
        "time": time,
        "switch": (phase < duty).astype(float),
        "inductor_current": inductor_current,
        "switch_current": switch_current,
        "diode_current": diode_current,
        "inductor_voltage": inductor_voltage,
        "output_voltage": output_voltage,
        "load_current": np.full_like(time, load_current),
        "capacitor_current": capacitor_current,
        "mode": mode,
        "theory": theory,
        "average_output_voltage": float(output_average),
        "current_ripple_pp": float(delta_i),
        "boundary_inductance": float(duty * (1.0 - duty) ** 2 * resistance / (2.0 * switching_frequency)),
        "metrics": waveform_metrics(output_voltage),
    }


def buck_boost_converter(
    time: np.ndarray,
    input_voltage: float,
    duty_cycle: float,
    switching_frequency: float,
    resistance: float,
    inductance: float,
    capacitance: float | None = None,
    mode: str = "CCM",
) -> dict[str, np.ndarray | float | dict[str, float]]:
    """Ideal inverting buck-boost converter waveforms for CCM or DCM."""
    duty = float(np.clip(duty_cycle, 0.0, 0.999))
    time = np.asarray(time, dtype=float)
    phase = _switch_phase(time, switching_frequency)
    ts = 1.0 / switching_frequency
    mode = mode.upper()
    k_value = 2.0 * inductance * switching_frequency / resistance

    if mode == "CCM":
        output_average = -(duty / (1.0 - duty)) * input_voltage
        load_current = abs(output_average) / resistance
        average_inductor_current = load_current / (1.0 - duty)
        delta_i = input_voltage * duty * ts / inductance
        i_min = average_inductor_current - 0.5 * delta_i
        i_peak = average_inductor_current + 0.5 * delta_i
        discharge_fraction = max(1.0 - duty, 1e-12)
        inductor_current = _current_ripple_profile(phase, duty, discharge_fraction, i_min, i_peak)
        diode_current = np.where(phase >= duty, inductor_current, 0.0)
        inductor_voltage = np.where(phase < duty, input_voltage, output_average)
    elif mode == "DCM":
        magnitude_ratio = duty / np.sqrt(max(k_value, 1e-12))
        output_average = -magnitude_ratio * input_voltage
        load_current = abs(output_average) / resistance
        i_peak = input_voltage * duty * ts / inductance
        discharge_fraction = duty / max(magnitude_ratio, 1e-12)
        inductor_current = _current_ripple_profile(phase, duty, discharge_fraction, 0.0, i_peak)
        diode_current = np.where((phase >= duty) & (phase < duty + discharge_fraction), inductor_current, 0.0)
        inductor_voltage = np.where(
            phase < duty,
            input_voltage,
            np.where(phase < duty + discharge_fraction, output_average, 0.0),
        )
        delta_i = i_peak
    else:
        raise ValueError("mode must be 'CCM' or 'DCM'.")

    switch_current = np.where(phase < duty, inductor_current, 0.0)
    capacitor_current = diode_current - load_current
    capacitor_voltage = _capacitor_voltage_from_current(time, capacitor_current, capacitance)
    output_voltage = output_average + capacitor_voltage
    theory = buck_boost_theory(input_voltage=input_voltage, duty_cycle=duty, mode=mode, k_value=k_value)

    return {
        "time": time,
        "switch": (phase < duty).astype(float),
        "inductor_current": inductor_current,
        "switch_current": switch_current,
        "diode_current": diode_current,
        "inductor_voltage": inductor_voltage,
        "output_voltage": output_voltage,
        "load_current": np.full_like(time, load_current),
        "capacitor_current": capacitor_current,
        "mode": mode,
        "theory": theory,
        "average_output_voltage": float(output_average),
        "current_ripple_pp": float(delta_i),
        "boundary_inductance": float((1.0 - duty) ** 2 * resistance / (2.0 * switching_frequency)),
        "metrics": waveform_metrics(output_voltage),
    }
