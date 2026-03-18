from __future__ import annotations

import numpy as np

TWO_PI = 2.0 * np.pi


def timebase(
    fundamental_frequency: float = 50.0,
    cycles: float = 1.0,
    samples_per_cycle: int = 2000,
    endpoint: bool = False,
) -> np.ndarray:
    """Generate a uniformly sampled time axis."""
    total_samples = max(int(np.ceil(cycles * samples_per_cycle)), 2)
    duration = cycles / fundamental_frequency
    return np.linspace(0.0, duration, total_samples, endpoint=endpoint)


def electrical_angle(time: np.ndarray, fundamental_frequency: float) -> np.ndarray:
    """Return the wrapped electrical angle for a time axis."""
    return np.mod(TWO_PI * fundamental_frequency * np.asarray(time, dtype=float), TWO_PI)


def sine_wave(
    time: np.ndarray,
    amplitude: float = 1.0,
    frequency: float = 50.0,
    phase: float = 0.0,
    offset: float = 0.0,
) -> np.ndarray:
    """Generate a sinusoid."""
    time = np.asarray(time, dtype=float)
    return offset + amplitude * np.sin(TWO_PI * frequency * time + phase)


def multi_phase_sine(
    time: np.ndarray,
    amplitude: float = 1.0,
    frequency: float = 50.0,
    phase_offsets: tuple[float, ...] = (0.0, -2.0 * np.pi / 3.0, 2.0 * np.pi / 3.0),
    offset: float = 0.0,
) -> np.ndarray:
    """Generate a stack of phase-shifted sine waves."""
    return np.vstack(
        [sine_wave(time, amplitude=amplitude, frequency=frequency, phase=phase, offset=offset) for phase in phase_offsets]
    )


def triangle_carrier(
    time: np.ndarray,
    frequency: float,
    amplitude: float = 1.0,
    phase: float = 0.0,
    offset: float = 0.0,
) -> np.ndarray:
    """Generate a symmetric triangle wave in the range [-amplitude, amplitude]."""
    time = np.asarray(time, dtype=float)
    normalized_phase = np.mod(frequency * time + phase / TWO_PI, 1.0)
    triangle = amplitude * (1.0 - 4.0 * np.abs(normalized_phase - 0.5))
    return triangle + offset


def comparator(
    reference: np.ndarray,
    carrier: np.ndarray,
    high_level: float = 1.0,
    low_level: float = 0.0,
) -> np.ndarray:
    """Compare two waveforms and emit a switching function."""
    reference = np.asarray(reference, dtype=float)
    carrier = np.asarray(carrier, dtype=float)
    return np.where(reference >= carrier, high_level, low_level)


def average_value(waveform: np.ndarray) -> float:
    """Return the arithmetic average of a waveform."""
    return float(np.mean(np.asarray(waveform, dtype=float)))


def rms_value(waveform: np.ndarray) -> float:
    """Return the RMS value of a waveform."""
    waveform = np.asarray(waveform, dtype=float)
    return float(np.sqrt(np.mean(np.square(waveform))))


def waveform_metrics(waveform: np.ndarray) -> dict[str, float]:
    """Return a standard metrics dictionary for any waveform."""
    waveform = np.asarray(waveform, dtype=float)
    return {
        "average": average_value(waveform),
        "rms": rms_value(waveform),
        "peak": float(np.max(waveform)),
        "minimum": float(np.min(waveform)),
        "peak_to_peak": float(np.ptp(waveform)),
    }


def modulation_index(reference_amplitude: float, carrier_amplitude: float = 1.0) -> float:
    """Compute the amplitude modulation index m_a."""
    return float(reference_amplitude / carrier_amplitude)


def frequency_ratio(carrier_frequency: float, fundamental_frequency: float) -> float:
    """Compute the frequency modulation ratio m_f."""
    return float(carrier_frequency / fundamental_frequency)
