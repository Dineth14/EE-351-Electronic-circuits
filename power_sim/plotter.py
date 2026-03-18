from __future__ import annotations

from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np


def to_omega_t(time: np.ndarray, fundamental_frequency: float) -> np.ndarray:
    """Convert time axis to electrical angle in radians."""
    return 2.0 * np.pi * fundamental_frequency * np.asarray(time, dtype=float)


def plot_stacked_waveforms(
    x: np.ndarray,
    traces: Iterable[dict],
    xlabel: str = "Time (s)",
    title: str | None = None,
    figsize: tuple[float, float] = (11.0, 8.0),
) -> tuple[plt.Figure, np.ndarray]:
    """Plot a set of aligned waveforms with a shared x-axis."""
    traces = list(traces)
    fig, axes = plt.subplots(len(traces), 1, figsize=figsize, sharex=True, constrained_layout=True)
    if len(traces) == 1:
        axes = np.array([axes])

    for axis, trace in zip(axes, traces):
        axis.plot(
            x,
            trace["y"],
            trace.get("style", "-"),
            color=trace.get("color"),
            linewidth=trace.get("linewidth", 2.0),
            label=trace.get("label"),
        )
        axis.set_ylabel(trace.get("ylabel", trace.get("label", "")))
        axis.grid(True, linestyle="--", alpha=0.35)
        if trace.get("label"):
            axis.legend(loc="upper right")

    axes[-1].set_xlabel(xlabel)
    if title:
        fig.suptitle(title)
    return fig, axes


def plot_voltage_current(
    x: np.ndarray,
    voltage: np.ndarray,
    current: np.ndarray,
    xlabel: str = "Time (s)",
    voltage_label: str = "Voltage",
    current_label: str = "Current",
    title: str | None = None,
    figsize: tuple[float, float] = (11.0, 6.0),
) -> tuple[plt.Figure, np.ndarray]:
    """Standard two-trace stacked plot for voltage and current waveforms."""
    traces = [
        {"y": np.asarray(voltage, dtype=float), "label": voltage_label, "ylabel": voltage_label, "color": "tab:blue"},
        {"y": np.asarray(current, dtype=float), "label": current_label, "ylabel": current_label, "color": "tab:red"},
    ]
    return plot_stacked_waveforms(x=x, traces=traces, xlabel=xlabel, title=title, figsize=figsize)
