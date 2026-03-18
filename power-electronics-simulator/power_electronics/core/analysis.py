"""Comprehensive signal, power quality, and converter analysis utilities.

Provides 20+ analysis functions covering FFT, THD, power factor, ripple,
efficiency, crest/form factors, transient metrics, component stress, Bode
response, and full power triangle decomposition.
"""

from __future__ import annotations

from typing import Iterable

import numpy as np
from scipy.signal import welch, windows

EPS = 1e-12


# ---------------------------------------------------------------------------
# Spectral Analysis
# ---------------------------------------------------------------------------

def compute_fft(
    signal: np.ndarray,
    fs: float,
    window: str = "hann",
    remove_dc: bool = True,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute single-sided FFT magnitude spectrum with optional windowing.

    Parameters
    ----------
    signal : np.ndarray
        Time-domain signal samples.
    fs : float
        Sampling frequency in Hz.
    window : str
        Window function name (any ``scipy.signal.windows`` name).
    remove_dc : bool
        Subtract signal mean before FFT.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        Frequency bins (Hz) and corresponding magnitudes.
    """
    n = signal.size
    x = signal - np.mean(signal) if remove_dc else signal.copy()
    win = windows.get_window(window, n)
    coherent_gain = np.mean(win)
    x *= win
    fft_vals = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(n, d=1.0 / fs)
    mags = 2.0 * np.abs(fft_vals) / max(n * coherent_gain, 1)
    return freqs, mags


def compute_fft_phase(
    signal: np.ndarray,
    fs: float,
    window: str = "hann",
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute single-sided FFT magnitude and phase spectra.

    Returns
    -------
    tuple[np.ndarray, np.ndarray, np.ndarray]
        Frequency bins (Hz), magnitudes, and phases (radians).
    """
    n = signal.size
    x = signal - np.mean(signal)
    win = windows.get_window(window, n)
    cg = np.mean(win)
    x *= win
    fft_vals = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(n, d=1.0 / fs)
    mags = 2.0 * np.abs(fft_vals) / max(n * cg, 1)
    phases = np.angle(fft_vals)
    return freqs, mags, phases


def compute_psd(
    signal: np.ndarray,
    fs: float,
    nperseg: int | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute power spectral density via Welch's method.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        Frequency bins (Hz) and PSD (V²/Hz).
    """
    seg = nperseg or min(1024, signal.size)
    return welch(signal, fs=fs, nperseg=seg)


def extract_harmonic(
    signal: np.ndarray,
    f0: float,
    fs: float,
    order: int = 1,
) -> tuple[float, float]:
    """Extract magnitude and phase of a specific harmonic order.

    Returns
    -------
    tuple[float, float]
        (magnitude, phase_radians)
    """
    freqs, mags, phases = compute_fft_phase(signal, fs)
    target = order * f0
    idx = int(np.argmin(np.abs(freqs - target)))
    return float(mags[idx]), float(phases[idx])


def compute_harmonic_spectrum(
    signal: np.ndarray,
    f0: float,
    fs: float,
    max_order: int = 50,
) -> tuple[np.ndarray, np.ndarray]:
    """Extract amplitudes at each harmonic order from 1 to max_order.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        Harmonic orders (1..max_order) and their magnitudes.
    """
    freqs, mags = compute_fft(signal, fs)
    orders = np.arange(1, max_order + 1)
    amps = np.array([
        float(mags[int(np.argmin(np.abs(freqs - k * f0)))])
        for k in orders
    ])
    return orders, amps


# ---------------------------------------------------------------------------
# THD and Distortion
# ---------------------------------------------------------------------------

def compute_thd(
    signal: np.ndarray,
    f0: float,
    fs: float,
    max_harmonic: int = 50,
) -> float:
    """Compute total harmonic distortion percentage (THD-F).

    THD-F = sqrt(sum(V_k^2, k=2..N)) / V_1 * 100
    """
    freqs, mags = compute_fft(signal, fs)
    if f0 <= 0:
        return 0.0

    def pick(order: int) -> float:
        target = order * f0
        idx = int(np.argmin(np.abs(freqs - target)))
        return float(mags[idx])

    fundamental = pick(1)
    if fundamental < EPS:
        return 0.0
    harmonic_rss = np.sqrt(sum(pick(k) ** 2 for k in range(2, max_harmonic + 1)))
    return float(100.0 * harmonic_rss / fundamental)


def compute_thd_r(
    signal: np.ndarray,
    f0: float,
    fs: float,
    max_harmonic: int = 50,
) -> float:
    """Compute THD-R (relative to total RMS including fundamental).

    THD-R = sqrt(sum(V_k^2, k=2..N)) / sqrt(sum(V_k^2, k=1..N)) * 100
    """
    freqs, mags = compute_fft(signal, fs)
    if f0 <= 0:
        return 0.0

    def pick(order: int) -> float:
        target = order * f0
        idx = int(np.argmin(np.abs(freqs - target)))
        return float(mags[idx])

    total_sq = sum(pick(k) ** 2 for k in range(1, max_harmonic + 1))
    fund_sq = pick(1) ** 2
    harm_sq = total_sq - fund_sq
    if total_sq < EPS:
        return 0.0
    return float(100.0 * np.sqrt(max(0.0, harm_sq)) / np.sqrt(total_sq))


def compute_individual_harmonic_distortion(
    signal: np.ndarray,
    f0: float,
    fs: float,
    max_harmonic: int = 25,
) -> dict[int, float]:
    """Compute per-harmonic distortion percentages relative to fundamental.

    Returns
    -------
    dict[int, float]
        {harmonic_order: distortion_percent}
    """
    orders, amps = compute_harmonic_spectrum(signal, f0, fs, max_harmonic)
    fund = amps[0] if amps[0] > EPS else 1.0
    return {int(k): float(100.0 * a / fund) for k, a in zip(orders, amps)}


# ---------------------------------------------------------------------------
# RMS and Basic Measurements
# ---------------------------------------------------------------------------

def compute_rms(signal: np.ndarray) -> float:
    """Compute root-mean-square value of a signal."""
    return float(np.sqrt(np.mean(signal ** 2)))


def compute_mean(signal: np.ndarray) -> float:
    """Compute arithmetic mean (DC component)."""
    return float(np.mean(signal))


def compute_peak_to_peak(signal: np.ndarray) -> float:
    """Compute peak-to-peak amplitude."""
    return float(np.max(signal) - np.min(signal))


def compute_crest_factor(signal: np.ndarray) -> float:
    """Compute crest factor (peak / RMS)."""
    rms = compute_rms(signal)
    if rms < EPS:
        return 0.0
    return float(np.max(np.abs(signal)) / rms)


def compute_form_factor(signal: np.ndarray) -> float:
    """Compute form factor (RMS / mean-absolute)."""
    mav = float(np.mean(np.abs(signal)))
    if mav < EPS:
        return 0.0
    return float(compute_rms(signal) / mav)


# ---------------------------------------------------------------------------
# Ripple Analysis
# ---------------------------------------------------------------------------

def compute_ripple(signal: np.ndarray) -> float:
    """Compute ripple ratio in percent (AC RMS / DC)."""
    dc = float(np.mean(signal))
    if abs(dc) < EPS:
        return 0.0
    ac_rms = float(np.sqrt(np.mean((signal - dc) ** 2)))
    return abs(100.0 * ac_rms / dc)


def compute_ripple_pp(signal: np.ndarray) -> float:
    """Compute peak-to-peak ripple ratio in percent (pp / DC)."""
    dc = float(np.mean(signal))
    if abs(dc) < EPS:
        return 0.0
    pp = float(np.max(signal) - np.min(signal))
    return abs(100.0 * pp / dc)


def compute_ripple_frequency(
    signal: np.ndarray,
    fs: float,
) -> float:
    """Estimate dominant ripple frequency from FFT peak of AC component."""
    ac = signal - np.mean(signal)
    freqs, mags = compute_fft(ac, fs, remove_dc=False)
    if len(mags) < 2:
        return 0.0
    idx = np.argmax(mags[1:]) + 1
    return float(freqs[idx])


# ---------------------------------------------------------------------------
# Power Analysis
# ---------------------------------------------------------------------------

def compute_efficiency(pin: float, pout: float) -> float:
    """Compute conversion efficiency percentage (clamped 0-100)."""
    if pin <= EPS:
        return 0.0
    return float(max(0.0, min(100.0, 100.0 * pout / pin)))


def compute_power_factor(voltage: np.ndarray, current: np.ndarray) -> float:
    """Compute true power factor (|P| / S) from full waveforms."""
    vrms = float(np.sqrt(np.mean(voltage ** 2)))
    irms = float(np.sqrt(np.mean(current ** 2)))
    if vrms < EPS or irms < EPS:
        return 0.0
    p = float(np.mean(voltage * current))
    return float(abs(np.clip(p / (vrms * irms), -1.0, 1.0)))


def compute_displacement_power_factor(
    voltage: np.ndarray,
    current: np.ndarray,
    f0: float,
    fs: float,
) -> float:
    """Compute displacement power factor cos(phi_1) at fundamental.

    Uses phase difference between fundamental components of V and I.
    """
    _, pv = extract_harmonic(voltage, f0, fs, order=1)
    _, pi = extract_harmonic(current, f0, fs, order=1)
    return float(np.cos(pv - pi))


def compute_power_triangle(
    voltage: np.ndarray,
    current: np.ndarray,
) -> dict[str, float]:
    """Full power triangle decomposition.

    Returns
    -------
    dict with keys:
        P_real_W, Q_reactive_VAR, S_apparent_VA, PF, D_distortion_VA
    """
    vrms = compute_rms(voltage)
    irms = compute_rms(current)
    s = vrms * irms
    p = float(np.mean(voltage * current))
    q_sq = max(0.0, s ** 2 - p ** 2)
    q = np.sqrt(q_sq)
    pf = abs(p / s) if s > EPS else 0.0
    return {
        "P_real_W": p,
        "Q_reactive_VAR": q,
        "S_apparent_VA": s,
        "PF": pf,
        "D_distortion_VA": 0.0,
    }


# ---------------------------------------------------------------------------
# Transient & Step Response Metrics
# ---------------------------------------------------------------------------

def compute_settling_time(
    signal: np.ndarray,
    time: np.ndarray,
    final_value: float | None = None,
    tolerance: float = 0.02,
) -> float:
    """Time to settle within ±tolerance of final value.

    Parameters
    ----------
    signal : np.ndarray
        Time-domain response.
    time : np.ndarray
        Time vector.
    final_value : float or None
        Steady-state target. If None, uses mean of last 10% of signal.
    tolerance : float
        Fractional band (e.g., 0.02 for ±2%).

    Returns
    -------
    float
        Settling time in seconds, or time[-1] if never settles.
    """
    if final_value is None:
        final_value = float(np.mean(signal[-max(10, len(signal) // 10):]))
    band = abs(final_value * tolerance) if abs(final_value) > EPS else tolerance
    within = np.abs(signal - final_value) <= band
    if np.all(within):
        return 0.0
    # Find last index OUTSIDE band, settling time is next sample after that
    outside_indices = np.where(~within)[0]
    if len(outside_indices) == 0:
        return 0.0
    last_outside = outside_indices[-1]
    if last_outside >= len(time) - 1:
        return float(time[-1])
    return float(time[last_outside + 1])


def compute_overshoot(
    signal: np.ndarray,
    final_value: float | None = None,
) -> float:
    """Compute percent overshoot above final value.

    Returns 0.0 if signal never exceeds final_value.
    """
    if final_value is None:
        final_value = float(np.mean(signal[-max(10, len(signal) // 10):]))
    if abs(final_value) < EPS:
        return 0.0
    peak = float(np.max(signal))
    if peak <= final_value:
        return 0.0
    return float(100.0 * (peak - final_value) / abs(final_value))


def compute_rise_time(
    signal: np.ndarray,
    time: np.ndarray,
    low_pct: float = 0.1,
    high_pct: float = 0.9,
) -> float:
    """Time for signal to go from low_pct to high_pct of final value.

    Returns time[-1] if thresholds are never crossed.
    """
    final = float(np.mean(signal[-max(10, len(signal) // 10):]))
    initial = float(signal[0])
    span = final - initial
    if abs(span) < EPS:
        return 0.0
    low_thresh = initial + low_pct * span
    high_thresh = initial + high_pct * span

    low_cross = np.where(signal >= low_thresh)[0]
    high_cross = np.where(signal >= high_thresh)[0]
    if len(low_cross) == 0 or len(high_cross) == 0:
        return float(time[-1])
    return float(time[high_cross[0]] - time[low_cross[0]])


# ---------------------------------------------------------------------------
# Component Stress Analysis
# ---------------------------------------------------------------------------

def compute_component_stress(
    voltage: np.ndarray,
    current: np.ndarray,
) -> dict[str, float]:
    """Compute voltage/current stress metrics for component selection.

    Returns
    -------
    dict with keys:
        V_peak, V_rms, I_peak, I_rms, I_avg, P_avg_W
    """
    return {
        "V_peak": float(np.max(np.abs(voltage))),
        "V_rms": compute_rms(voltage),
        "I_peak": float(np.max(np.abs(current))),
        "I_rms": compute_rms(current),
        "I_avg": float(np.mean(np.abs(current))),
        "P_avg_W": float(np.mean(voltage * current)),
    }


def compute_switch_utilization(
    voltage_rating: float,
    current_rating: float,
    output_power: float,
) -> float:
    """Switch utilization factor = P_out / (V_rated * I_rated).

    A higher value indicates better utilization of semiconductor ratings.
    """
    denom = voltage_rating * current_rating
    if denom < EPS:
        return 0.0
    return float(output_power / denom)


# ---------------------------------------------------------------------------
# Bode / Frequency Response
# ---------------------------------------------------------------------------

def compute_bode_response(
    num_coeffs: list[float],
    den_coeffs: list[float],
    freq_range: tuple[float, float] = (1.0, 1e6),
    num_points: int = 500,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute Bode magnitude and phase from transfer function polynomial coefficients.

    Parameters
    ----------
    num_coeffs : list[float]
        Numerator polynomial coefficients [a_n, a_{n-1}, ..., a_0].
    den_coeffs : list[float]
        Denominator polynomial coefficients [b_m, b_{m-1}, ..., b_0].
    freq_range : tuple[float, float]
        (f_min_Hz, f_max_Hz) for logarithmic sweep.
    num_points : int
        Number of frequency points.

    Returns
    -------
    tuple[np.ndarray, np.ndarray, np.ndarray]
        Frequencies (Hz), magnitude (dB), phase (degrees).
    """
    freqs = np.logspace(np.log10(freq_range[0]), np.log10(freq_range[1]), num_points)
    s = 1j * 2.0 * np.pi * freqs
    num = np.polyval(num_coeffs, s)
    den = np.polyval(den_coeffs, s)
    h = num / np.where(np.abs(den) < EPS, EPS, den)
    mag_db = 20.0 * np.log10(np.maximum(np.abs(h), EPS))
    phase_deg = np.degrees(np.unwrap(np.angle(h)))
    return freqs, mag_db, phase_deg


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def summarize_metrics(values: Iterable[tuple[str, float]]) -> dict[str, float]:
    """Build a float-only metrics dictionary from name-value pairs."""
    return {name: float(value) for name, value in values}


def compute_full_analysis(
    time: np.ndarray,
    voltage: np.ndarray,
    current: np.ndarray,
    f0: float,
) -> dict[str, float]:
    """All-in-one analysis returning a comprehensive metrics dictionary.

    Computes RMS, THD, power triangle, ripple, crest/form factors, and
    transient metrics in a single call.

    Parameters
    ----------
    time : np.ndarray
        Time vector in seconds.
    voltage : np.ndarray
        Voltage waveform.
    current : np.ndarray
        Current waveform.
    f0 : float
        Fundamental frequency in Hz.

    Returns
    -------
    dict[str, float]
        Comprehensive metric dictionary.
    """
    fs = 1.0 / max(time[1] - time[0], EPS) if len(time) > 1 else 1.0
    pt = compute_power_triangle(voltage, current)
    return {
        "V_rms": compute_rms(voltage),
        "I_rms": compute_rms(current),
        "V_dc": compute_mean(voltage),
        "I_dc": compute_mean(current),
        "V_pp": compute_peak_to_peak(voltage),
        "I_pp": compute_peak_to_peak(current),
        "V_thd_%": compute_thd(voltage, f0, fs),
        "I_thd_%": compute_thd(current, f0, fs),
        "V_ripple_%": compute_ripple(voltage),
        "crest_factor": compute_crest_factor(voltage),
        "form_factor": compute_form_factor(voltage),
        "power_factor": compute_power_factor(voltage, current),
        **pt,
        "settling_time_s": compute_settling_time(voltage, time),
        "overshoot_%": compute_overshoot(voltage),
        "rise_time_s": compute_rise_time(voltage, time),
    }
