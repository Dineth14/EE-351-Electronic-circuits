"""Static matplotlib plotting helpers for publication-quality figures."""

from __future__ import annotations

from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np


def plot_publication_waveforms(
    time: np.ndarray,
    signals: dict[str, np.ndarray],
    signal_names: Iterable[str] | None = None,
) -> plt.Figure:
    """Create stacked waveform plots suitable for reports.

    Parameters
    ----------
    time:
        Time array in seconds.
    signals:
        Dictionary of waveform arrays.
    signal_names:
        Optional ordered subset of signals to plot.
    """
    names = list(signal_names) if signal_names is not None else list(signals.keys())
    n = len(names)
    fig, axes = plt.subplots(n, 1, figsize=(12, max(3, 2.0 * n)), sharex=True)
    if n == 1:
        axes = [axes]
    for ax, name in zip(axes, names):
        ax.plot(time, signals[name], linewidth=1.2)
        ax.set_ylabel(name)
        ax.grid(True, alpha=0.35)
    axes[-1].set_xlabel("Time (s)")
    fig.tight_layout()
    return fig
