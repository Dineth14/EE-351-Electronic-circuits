"""Signal and power quality analysis utilities."""

from __future__ import annotations

from typing import Iterable

import numpy as np


EPS = 1e-12


def compute_fft(signal: np.ndarray, fs: float) -> tuple[np.ndarray, np.ndarray]:
    """Compute single-sided FFT magnitude spectrum.

    Parameters
    ----------
    signal:
        Time-domain signal samples.
    fs:
        Sampling frequency in Hz.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        Frequency bins in Hz and corresponding magnitudes.
    """
    n = signal.size
    centered = signal - np.mean(signal)
    fft_vals = np.fft.rfft(centered)
    freqs = np.fft.rfftfreq(n, d=1.0 / fs)
    mags = 2.0 * np.abs(fft_vals) / max(n, 1)
    return freqs, mags


def compute_thd(signal: np.ndarray, f0: float, fs: float, max_harmonic: int = 50) -> float:
    """Compute total harmonic distortion percentage.

    Parameters
    ----------
    signal:
        Time-domain signal.
    f0:
        Fundamental frequency in Hz.
    fs:
        Sampling frequency in Hz.
    max_harmonic:
        Highest harmonic order to include.

    Returns
    -------
    float
        THD in percent.
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


def compute_ripple(signal: np.ndarray) -> float:
    """Compute ripple ratio in percent relative to average absolute value."""
    dc = float(np.mean(signal))
    if abs(dc) < EPS:
        return 0.0
    ac_rms = float(np.sqrt(np.mean((signal - dc) ** 2)))
    return abs(100.0 * ac_rms / dc)


def compute_efficiency(pin: float, pout: float) -> float:
    """Compute conversion efficiency percentage."""
    if pin <= EPS:
        return 0.0
    return float(max(0.0, min(100.0, 100.0 * pout / pin)))


def compute_power_factor(voltage: np.ndarray, current: np.ndarray) -> float:
    """Compute displacement-inclusive power factor from sampled waveforms."""
    vrms = float(np.sqrt(np.mean(voltage**2)))
    irms = float(np.sqrt(np.mean(current**2)))
    if vrms < EPS or irms < EPS:
        return 0.0
    p = float(np.mean(voltage * current))
    # Report magnitude PF for display consistency across operating quadrants.
    return float(abs(np.clip(p / (vrms * irms), -1.0, 1.0)))


def summarize_metrics(values: Iterable[tuple[str, float]]) -> dict[str, float]:
    """Build a float-only metrics dictionary."""
    return {name: float(value) for name, value in values}
