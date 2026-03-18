"""Comprehensive tests for core analysis utilities."""

from __future__ import annotations

import numpy as np
import pytest
from numpy.testing import assert_allclose

from power_electronics.core.analysis import (
    compute_bode_response,
    compute_component_stress,
    compute_crest_factor,
    compute_displacement_power_factor,
    compute_efficiency,
    compute_fft,
    compute_fft_phase,
    compute_form_factor,
    compute_full_analysis,
    compute_harmonic_spectrum,
    compute_individual_harmonic_distortion,
    compute_mean,
    compute_overshoot,
    compute_peak_to_peak,
    compute_power_factor,
    compute_power_triangle,
    compute_psd,
    compute_ripple,
    compute_ripple_frequency,
    compute_ripple_pp,
    compute_rise_time,
    compute_rms,
    compute_settling_time,
    compute_switch_utilization,
    compute_thd,
    compute_thd_r,
    extract_harmonic,
    summarize_metrics,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sine_50hz():
    """1-second 50 Hz sine at 10 kHz sample rate."""
    fs = 10_000.0
    t = np.linspace(0.0, 1.0, int(fs))
    sig = np.sin(2.0 * np.pi * 50.0 * t)
    return t, sig, fs


@pytest.fixture
def distorted_50hz():
    """50 Hz + 10% 3rd harmonic."""
    fs = 10_000.0
    t = np.linspace(0.0, 1.0, int(fs))
    sig = np.sin(2.0 * np.pi * 50.0 * t) + 0.1 * np.sin(2.0 * np.pi * 150.0 * t)
    return t, sig, fs


@pytest.fixture
def dc_with_ripple():
    """12 V DC + 0.3 V ripple at 1 kHz."""
    fs = 50_000.0
    t = np.linspace(0.0, 0.1, int(fs * 0.1))
    sig = 12.0 + 0.3 * np.sin(2.0 * np.pi * 1000.0 * t)
    return t, sig, fs


# ---------------------------------------------------------------------------
# FFT Tests
# ---------------------------------------------------------------------------

class TestFFT:
    def test_fft_returns_correct_lengths(self, sine_50hz):
        _, sig, fs = sine_50hz
        freqs, mags = compute_fft(sig, fs)
        assert len(freqs) == len(mags)
        assert len(freqs) > 0

    def test_fft_peak_at_fundamental(self, sine_50hz):
        _, sig, fs = sine_50hz
        freqs, mags = compute_fft(sig, fs)
        peak_idx = np.argmax(mags)
        assert_allclose(freqs[peak_idx], 50.0, atol=2.0)

    def test_fft_with_different_windows(self, sine_50hz):
        _, sig, fs = sine_50hz
        for win in ("hann", "hamming", "boxcar"):
            freqs, mags = compute_fft(sig, fs, window=win)
            assert len(freqs) == len(mags)

    def test_fft_remove_dc_false(self):
        sig = np.ones(1000) * 5.0
        freqs, mags = compute_fft(sig, 1000.0, remove_dc=False)
        assert mags[0] > 0

    def test_fft_phase_returns_three_arrays(self, sine_50hz):
        _, sig, fs = sine_50hz
        freqs, mags, phases = compute_fft_phase(sig, fs)
        assert len(freqs) == len(mags) == len(phases)


class TestPSD:
    def test_psd_returns_positive(self, sine_50hz):
        _, sig, fs = sine_50hz
        f, pxx = compute_psd(sig, fs)
        assert np.all(pxx >= 0)
        assert len(f) == len(pxx)

    def test_psd_peak_near_fundamental(self, sine_50hz):
        _, sig, fs = sine_50hz
        f, pxx = compute_psd(sig, fs)
        peak_f = f[np.argmax(pxx)]
        assert abs(peak_f - 50.0) < 10.0


class TestHarmonics:
    def test_extract_harmonic_fundamental(self, sine_50hz):
        _, sig, fs = sine_50hz
        mag, phase = extract_harmonic(sig, 50.0, fs, order=1)
        assert mag > 0.5  # should be close to 1.0 for pure sine

    def test_harmonic_spectrum_shape(self, distorted_50hz):
        _, sig, fs = distorted_50hz
        orders, amps = compute_harmonic_spectrum(sig, 50.0, fs, max_order=10)
        assert len(orders) == 10
        assert len(amps) == 10
        assert orders[0] == 1

    def test_harmonic_spectrum_fundamental_dominant(self, distorted_50hz):
        _, sig, fs = distorted_50hz
        orders, amps = compute_harmonic_spectrum(sig, 50.0, fs, max_order=10)
        assert amps[0] > amps[2]  # fundamental > 3rd harmonic


# ---------------------------------------------------------------------------
# THD Tests
# ---------------------------------------------------------------------------

class TestTHD:
    def test_pure_sine_low_thd(self, sine_50hz):
        _, sig, fs = sine_50hz
        thd = compute_thd(sig, 50.0, fs)
        assert thd < 1.0  # near-zero for pure sine

    def test_distorted_signal_nonzero_thd(self, distorted_50hz):
        _, sig, fs = distorted_50hz
        thd = compute_thd(sig, 50.0, fs)
        assert thd > 5.0  # ~10% 3rd harmonic → ~10% THD

    def test_thd_zero_frequency(self):
        sig = np.random.randn(1000)
        assert compute_thd(sig, 0.0, 1000.0) == 0.0

    def test_thd_r_less_than_thd_f(self, distorted_50hz):
        _, sig, fs = distorted_50hz
        thd_f = compute_thd(sig, 50.0, fs)
        thd_r = compute_thd_r(sig, 50.0, fs)
        assert thd_r <= thd_f

    def test_individual_harmonic_distortion(self, distorted_50hz):
        _, sig, fs = distorted_50hz
        ihd = compute_individual_harmonic_distortion(sig, 50.0, fs, max_harmonic=5)
        assert isinstance(ihd, dict)
        assert 1 in ihd
        assert ihd[1] == pytest.approx(100.0, abs=5.0)  # fundamental = 100%


# ---------------------------------------------------------------------------
# RMS & Basic
# ---------------------------------------------------------------------------

class TestBasicMeasurements:
    def test_rms_of_sine(self, sine_50hz):
        _, sig, _ = sine_50hz
        assert_allclose(compute_rms(sig), 1.0 / np.sqrt(2), rtol=0.01)

    def test_mean_of_sine_near_zero(self, sine_50hz):
        _, sig, _ = sine_50hz
        assert abs(compute_mean(sig)) < 0.01

    def test_peak_to_peak_of_sine(self, sine_50hz):
        _, sig, _ = sine_50hz
        assert_allclose(compute_peak_to_peak(sig), 2.0, atol=0.02)

    def test_crest_factor_of_sine(self, sine_50hz):
        _, sig, _ = sine_50hz
        cf = compute_crest_factor(sig)
        assert_allclose(cf, np.sqrt(2), rtol=0.02)

    def test_form_factor_of_sine(self, sine_50hz):
        _, sig, _ = sine_50hz
        ff = compute_form_factor(sig)
        assert ff > 1.0  # for sine, ~1.11

    def test_crest_factor_zero_signal(self):
        assert compute_crest_factor(np.zeros(100)) == 0.0

    def test_form_factor_zero_signal(self):
        assert compute_form_factor(np.zeros(100)) == 0.0


# ---------------------------------------------------------------------------
# Ripple Tests
# ---------------------------------------------------------------------------

class TestRipple:
    def test_ripple_of_dc_with_ac(self, dc_with_ripple):
        _, sig, _ = dc_with_ripple
        rip = compute_ripple(sig)
        assert rip > 0
        assert rip < 10.0  # 0.3V on 12V ~ 2.5%

    def test_ripple_pp(self, dc_with_ripple):
        _, sig, _ = dc_with_ripple
        rip_pp = compute_ripple_pp(sig)
        assert rip_pp > 0
        assert rip_pp > compute_ripple(sig)  # pp > rms always

    def test_ripple_frequency_detection(self, dc_with_ripple):
        _, sig, fs = dc_with_ripple
        f_rip = compute_ripple_frequency(sig, fs)
        assert abs(f_rip - 1000.0) < 100.0

    def test_ripple_zero_dc(self):
        sig = np.zeros(100)
        assert compute_ripple(sig) == 0.0
        assert compute_ripple_pp(sig) == 0.0


# ---------------------------------------------------------------------------
# Power Tests
# ---------------------------------------------------------------------------

class TestPower:
    def test_efficiency_basic(self):
        assert compute_efficiency(100.0, 90.0) == 90.0

    def test_efficiency_clamped(self):
        assert compute_efficiency(100.0, 150.0) == 100.0
        assert compute_efficiency(0.0, 10.0) == 0.0

    def test_power_factor_in_phase(self, sine_50hz):
        _, sig, _ = sine_50hz
        pf = compute_power_factor(sig, sig)
        assert_allclose(pf, 1.0, atol=0.01)

    def test_power_factor_quadrature(self, sine_50hz):
        t, sig, _ = sine_50hz
        sig90 = np.cos(2.0 * np.pi * 50.0 * t)
        pf = compute_power_factor(sig, sig90)
        assert pf < 0.1  # near zero for 90° out of phase

    def test_displacement_power_factor(self, sine_50hz):
        t, sig, fs = sine_50hz
        dpf = compute_displacement_power_factor(sig, sig, 50.0, fs)
        assert_allclose(dpf, 1.0, atol=0.1)

    def test_power_triangle_keys(self, sine_50hz):
        _, sig, _ = sine_50hz
        pt = compute_power_triangle(sig, sig)
        for k in ("P_real_W", "Q_reactive_VAR", "S_apparent_VA", "PF"):
            assert k in pt

    def test_power_triangle_real_power(self, sine_50hz):
        _, sig, _ = sine_50hz
        pt = compute_power_triangle(sig, sig)
        assert pt["P_real_W"] > 0
        assert pt["PF"] > 0.9


# ---------------------------------------------------------------------------
# Transient Tests
# ---------------------------------------------------------------------------

class TestTransient:
    def test_settling_time_already_settled(self):
        t = np.linspace(0, 1, 1000)
        sig = np.ones(1000) * 5.0
        assert compute_settling_time(sig, t, final_value=5.0) == 0.0

    def test_settling_time_with_transient(self):
        t = np.linspace(0, 1, 1000)
        sig = 5.0 * (1 - np.exp(-10 * t))  # fast exponential rise
        ts = compute_settling_time(sig, t, final_value=5.0, tolerance=0.02)
        assert ts > 0
        assert ts < 1.0

    def test_overshoot_no_overshoot(self):
        sig = np.linspace(0, 5, 1000)
        assert compute_overshoot(sig, final_value=5.0) == 0.0

    def test_overshoot_with_overshoot(self):
        t = np.linspace(0, 1, 1000)
        sig = 5.0 * (1 - 1.5 * np.exp(-10 * t) * np.cos(20 * t))
        os = compute_overshoot(sig, final_value=5.0)
        assert os > 0

    def test_rise_time_step_response(self):
        t = np.linspace(0, 1, 10000)
        sig = 5.0 * (1 - np.exp(-20 * t))
        rt = compute_rise_time(sig, t)
        assert rt > 0
        assert rt < 0.5


# ---------------------------------------------------------------------------
# Component Stress
# ---------------------------------------------------------------------------

class TestComponentStress:
    def test_stress_keys(self, sine_50hz):
        _, sig, _ = sine_50hz
        stress = compute_component_stress(sig, sig)
        for k in ("V_peak", "V_rms", "I_peak", "I_rms", "I_avg", "P_avg_W"):
            assert k in stress

    def test_switch_utilization(self):
        su = compute_switch_utilization(600.0, 10.0, 1000.0)
        assert_allclose(su, 1000.0 / 6000.0, rtol=0.01)

    def test_switch_utilization_zero(self):
        assert compute_switch_utilization(0.0, 10.0, 100.0) == 0.0


# ---------------------------------------------------------------------------
# Bode Response
# ---------------------------------------------------------------------------

class TestBode:
    def test_bode_shapes(self):
        freqs, mag_db, phase_deg = compute_bode_response([1.0], [1.0, 1.0])
        assert len(freqs) == len(mag_db) == len(phase_deg)

    def test_bode_low_pass_rolloff(self):
        # Simple RC: H(s) = 1 / (s + 1)
        freqs, mag_db, _ = compute_bode_response([1.0], [1.0, 1.0])
        # At very low freq, gain ~ 0 dB; at high freq, gain drops
        assert mag_db[0] > mag_db[-1]

    def test_bode_custom_freq_range(self):
        freqs, mag_db, phase_deg = compute_bode_response(
            [1.0], [1.0, 1.0], freq_range=(10.0, 1e4), num_points=100
        )
        assert len(freqs) == 100
        assert freqs[0] == pytest.approx(10.0, rel=0.1)


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

class TestUtility:
    def test_summarize_metrics(self):
        result = summarize_metrics([("a", 1.5), ("b", 2)])
        assert result == {"a": 1.5, "b": 2.0}

    def test_full_analysis_keys(self, sine_50hz):
        t, sig, _ = sine_50hz
        result = compute_full_analysis(t, sig, sig, 50.0)
        expected_keys = [
            "V_rms", "I_rms", "V_dc", "I_dc", "V_pp", "I_pp",
            "V_thd_%", "I_thd_%", "V_ripple_%",
            "crest_factor", "form_factor", "power_factor",
            "P_real_W", "Q_reactive_VAR", "S_apparent_VA", "PF",
            "settling_time_s", "overshoot_%", "rise_time_s",
        ]
        for k in expected_keys:
            assert k in result, f"Missing key: {k}"

    def test_full_analysis_finite(self, sine_50hz):
        t, sig, _ = sine_50hz
        result = compute_full_analysis(t, sig, sig, 50.0)
        for k, v in result.items():
            assert np.isfinite(v), f"Non-finite value for {k}: {v}"
