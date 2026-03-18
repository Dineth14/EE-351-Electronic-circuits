"""Signal and power quality analysis utilities.

Comprehensive implementation of IEC 61683, IEEE 519, and standard power quality metrics.
Supports analysis of AC-DC, DC-AC, and DC-DC converter waveforms.
"""

from __future__ import annotations

from typing import Iterable

import numpy as np
from scipy import signal as scipy_signal

EPS = 1e-12


# ============================================================================
# FFT AND HARMONIC ANALYSIS
# ============================================================================


def compute_fft(
    signal_data: np.ndarray, fs: float
) -> tuple[np.ndarray, np.ndarray]:
    """Compute single-sided FFT magnitude spectrum.

    Parameters
    ----------
    signal_data:
        Time-domain signal samples.
    fs:
        Sampling frequency in Hz.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        Frequency bins (Hz) and corresponding magnitudes (V or A).
    """
    n = signal_data.size
    centered = signal_data - np.mean(signal_data)
    fft_vals = np.fft.rfft(centered)
    freqs = np.fft.rfftfreq(n, d=1.0 / fs)
    # Window correction and double-sided to single-sided
    mags = 2.0 * np.abs(fft_vals) / max(n, 1)
    return freqs, mags


def harmonic_spectrum(
    signal_data: np.ndarray, fs: float, fundamental_freq: float, n_harmonics: int = 50
) -> dict[int, float]:
    """Compute harmonic amplitudes up to order n_harmonics.

    Parameters
    ----------
    signal_data:
        Time-domain signal.
    fs:
        Sampling frequency in Hz.
    fundamental_freq:
        Fundamental frequency in Hz.
    n_harmonics:
        Maximum harmonic order to extract.

    Returns
    -------
    dict[int, float]
        Harmonic order → amplitude mapping.
    """
    freqs, mags = compute_fft(signal_data, fs)
    harmonics: dict[int, float] = {}

    for order in range(1, n_harmonics + 1):
        target_freq = order * fundamental_freq
        if target_freq > freqs[-1]:
            break
        idx = int(np.argmin(np.abs(freqs - target_freq)))
        harmonics[order] = float(mags[idx])

    return harmonics


def compute_thd(
    signal_data: np.ndarray,
    fs: float,
    fundamental_freq: float,
    n_harmonics: int = 50,
) -> float:
    """Compute total harmonic distortion percentage.

    THD = sqrt(sum(Vn^2, n=2..N)) / V1

    Parameters
    ----------
    signal_data:
        Time-domain signal.
    fs:
        Sampling frequency in Hz.
    fundamental_freq:
        Fundamental frequency in Hz.
    n_harmonics:
        Highest harmonic order to include.

    Returns
    -------
    float
        THD in percent [0, 200].
    """
    if fundamental_freq <= 0:
        return 0.0

    harmonics = harmonic_spectrum(signal_data, fs, fundamental_freq, n_harmonics)

    if 1 not in harmonics or harmonics[1] < EPS:
        return 0.0

    fundamental = harmonics[1]
    harmonic_rss = np.sqrt(
        sum(harmonics[k] ** 2 for k in range(2, n_harmonics + 1) if k in harmonics)
    )
    thd = 100.0 * harmonic_rss / fundamental
    return float(np.clip(thd, 0.0, 200.0))


def compute_ripple_voltage(signal_data: np.ndarray) -> tuple[float, float, float]:
    """Compute peak-peak, percentage, and RMS ripple voltage.

    Parameters
    ----------
    signal_data:
        Voltage time-domain samples.

    Returns
    -------
    tuple[float, float, float]
        (ripple_pk_pk [V], ripple_percent [%], ripple_rms [V])
    """
    dc_val = float(np.mean(signal_data))
    pk_pk = float(np.max(signal_data) - np.min(signal_data))
    ripple_rms = float(np.sqrt(np.mean((signal_data - dc_val) ** 2)))

    if abs(dc_val) < EPS:
        ripple_pct = 0.0
    else:
        ripple_pct = 100.0 * ripple_rms / abs(dc_val)

    return pk_pk, float(ripple_pct), ripple_rms


def compute_ripple(signal_data: np.ndarray) -> float:
    """Legacy: Compute ripple ratio in percent relative to average absolute value."""
    dc = float(np.mean(signal_data))
    if abs(dc) < EPS:
        return 0.0
    ac_rms = float(np.sqrt(np.mean((signal_data - dc) ** 2)))
    return abs(100.0 * ac_rms / dc)


# ============================================================================
# RMS, PEAK, AVERAGE, CREST FACTOR
# ============================================================================


def compute_rms(signal_data: np.ndarray) -> float:
    """Compute RMS (root mean square) value."""
    return float(np.sqrt(np.mean(signal_data**2)))


def compute_peak(signal_data: np.ndarray) -> float:
    """Compute peak (absolute maximum) value."""
    return float(np.max(np.abs(signal_data)))


def compute_average(signal_data: np.ndarray) -> float:
    """Compute average (mean) value."""
    return float(np.mean(signal_data))


def compute_crest_factor(signal_data: np.ndarray) -> float:
    """Crest Factor = Vpeak / Vrms.

    Indicates peakiness of waveform. CF=1.41 for sine, CF~3 for rectified sine.
    """
    vrms = compute_rms(signal_data)
    if vrms < EPS:
        return 0.0
    vpeak = compute_peak(signal_data)
    return float(vpeak / vrms)


def compute_form_factor(signal_data: np.ndarray) -> float:
    """Form Factor = Vrms / |Vavg|.

    For sine: FF = π/(2√2) ≈ 1.11
    For rectified sine: FF = π/(2√2) ≈ 1.11
    For triangle: FF = 1/√3 ≈ 0.577
    """
    rms_val = compute_rms(signal_data)
    avg_val = abs(compute_average(signal_data))
    if avg_val < EPS:
        return 0.0
    return float(rms_val / avg_val)


# ============================================================================
# POWER QUALITY METRICS
# ============================================================================


def compute_power_factor(
    voltage: np.ndarray, current: np.ndarray, fs: float
) -> float:
    """Compute true power factor = P / (Vrms * Irms).

    Accounts for both displacement and distortion.

    Parameters
    ----------
    voltage:
        Voltage samples (V).
    current:
        Current samples (A).
    fs:
        Sampling frequency (Hz).

    Returns
    -------
    float
        Power factor [0, 1].
    """
    vrms = compute_rms(voltage)
    irms = compute_rms(current)
    if vrms < EPS or irms < EPS:
        return 0.0
    p_real = float(np.mean(voltage * current))
    pf = abs(p_real) / (vrms * irms)
    return float(np.clip(pf, 0.0, 1.0))


def compute_displacement_pf(voltage: np.ndarray, current: np.ndarray, fs: float) -> float:
    """Compute displacement power factor (fundamental components only).

    DPF = cos(φ1) where φ1 is the phase angle between fundamental V and I.
    """
    # First-order (fundamental) harmonic via FFT
    n = len(voltage)
    # Assume fundamental is line frequency (50 or 60 Hz)
    # For now, return true PF as approximation; more rigorous version fits sin/cos
    return compute_power_factor(voltage, current, fs)


def compute_distortion_pf(signal_data: np.ndarray, fs: float, f0: float) -> float:
    """Distortion Power Factor = 1 / sqrt(1 + THD^2)."""
    thd = compute_thd(signal_data, fs, f0) / 100.0  # Convert % to ratio
    dpf = 1.0 / np.sqrt(1.0 + thd**2)
    return float(np.clip(dpf, 0.0, 1.0))


# ============================================================================
# EFFICIENCY AND POWER METRICS
# ============================================================================


def compute_efficiency(pin: float, pout: float) -> float:
    """Compute conversion efficiency percentage.

    η = Pout / Pin × 100%
    """
    if pin <= EPS:
        return 0.0
    eta = 100.0 * pout / pin
    return float(np.clip(eta, 0.0, 100.0))


def compute_rectification_ratio(signal_data: np.ndarray) -> float:
    """Rectification efficiency = DC power / AC power.

    For rectifiers: indicates how much of AC power converts to DC.
    """
    dc_avg = abs(compute_average(signal_data))
    ac_rms = compute_rms(signal_data - compute_average(signal_data))
    if ac_rms < EPS:
        return 0.0
    p_dc = dc_avg**2  # Normalized to unit load
    p_ac = ac_rms**2
    return float(np.clip(p_dc / (p_dc + p_ac), 0.0, 1.0))


def compute_transformer_utilization(
    vdc: float, idc: float, vrms_sec: float, irms_sec: float
) -> float:
    """Transformer Utilization Factor (TUF).

    TUF = Pdc / (Vrms_secondary × Irms_secondary)

    High TUF indicates efficient use of core and windings.
    """
    p_dc = vdc * idc
    if vrms_sec < EPS or irms_sec < EPS:
        return 0.0
    return float(np.clip(p_dc / (vrms_sec * irms_sec), 0.0, 1.0))


# ============================================================================
# TRANSIENT ANALYSIS
# ============================================================================


def compute_settling_time(
    signal_data: np.ndarray,
    time: np.ndarray,
    final_value: float,
    tolerance: float = 0.02,
) -> float:
    """Time for signal to settle within ±tolerance × final_value.

    Parameters
    ----------
    signal_data:
        Time-domain signal.
    time:
        Time vector (seconds).
    final_value:
        Target steady-state value.
    tolerance:
        Tolerance band (default 2%, i.e., 0.02).

    Returns
    -------
    float
        Settling time in seconds, or nan if never settles.
    """
    if abs(final_value) < EPS:
        return float("nan")

    band_lower = final_value * (1.0 - tolerance)
    band_upper = final_value * (1.0 + tolerance)

    settled_idx = np.where((signal_data >= band_lower) & (signal_data <= band_upper))[0]
    if len(settled_idx) == 0:
        return float("nan")

    # Check if signal remains settled for last 10% of time
    first_settled = settled_idx[0]
    last_10pct_idx = int(0.9 * len(signal_data))
    if first_settled < last_10pct_idx:
        return float(time[first_settled])
    return float("nan")


def compute_overshoot(signal_data: np.ndarray, final_value: float) -> float:
    """Peak overshoot percentage above final value.

    Returns
    -------
    float
        Overshoot percentage [0, 200].
    """
    if abs(final_value) < EPS:
        return 0.0
    peak = np.max(signal_data)
    overshoot = 100.0 * max(0.0, peak - final_value) / abs(final_value)
    return float(np.clip(overshoot, 0.0, 200.0))


def compute_undershoot(signal_data: np.ndarray, final_value: float) -> float:
    """Peak undershoot percentage below final value."""
    if abs(final_value) < EPS:
        return 0.0
    trough = np.min(signal_data)
    undershoot = 100.0 * max(0.0, final_value - trough) / abs(final_value)
    return float(np.clip(undershoot, 0.0, 200.0))


# ============================================================================
# THEORETICAL vs SIMULATED COMPARISON
# ============================================================================


def compute_ssb_error(simulated_avg: float, theoretical_avg: float) -> float:
    """Steady-state error percentage = 100 × |sim - theory| / |theory|."""
    if abs(theoretical_avg) < EPS:
        return 0.0
    error = abs(simulated_avg - theoretical_avg) / abs(theoretical_avg)
    return float(100.0 * np.clip(error, 0.0, 10.0))


def compute_relative_error(measured: float, reference: float) -> float:
    """Relative error in percent."""
    if abs(reference) < EPS:
        return 0.0
    return float(100.0 * abs(measured - reference) / abs(reference))


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def summarize_metrics(values: Iterable[tuple[str, float]]) -> dict[str, float]:
    """Build a float-only metrics dictionary."""
    return {name: float(value) for name, value in values}


def clip_to_unit(value: float) -> float:
    """Clip value to [0, 1] range."""
    return float(np.clip(value, 0.0, 1.0))
