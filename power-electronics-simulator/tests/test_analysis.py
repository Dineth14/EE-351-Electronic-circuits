"""Tests for core analysis utilities."""

from __future__ import annotations

import numpy as np

from power_electronics.core.analysis import (
    compute_efficiency,
    compute_fft,
    compute_power_factor,
    compute_ripple,
    compute_thd,
)


def test_analysis_functions() -> None:
    fs = 10000.0
    t = np.linspace(0.0, 0.1, 5000)
    sig = np.sin(2.0 * np.pi * 50.0 * t) + 0.1 * np.sin(2.0 * np.pi * 150.0 * t)
    freqs, mags = compute_fft(sig, fs)
    assert len(freqs) == len(mags)
    assert compute_thd(sig, 50.0, fs) > 0
    assert compute_ripple(np.ones_like(sig) * 10.0 + 0.1 * sig) > 0
    assert compute_efficiency(100.0, 90.0) == 90.0
    assert 0.0 <= compute_power_factor(np.sin(t), np.sin(t - 0.1)) <= 1.0
