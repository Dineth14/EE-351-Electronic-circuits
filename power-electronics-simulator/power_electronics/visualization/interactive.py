"""Plotly-based interactive chart generation."""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from power_electronics.core.analysis import compute_fft, compute_thd
from power_electronics.visualization.themes import THEMES


def build_waveform_figure(
    time: np.ndarray,
    signals: dict[str, np.ndarray],
    selected_signals: list[str] | None = None,
    theme: str = "oscilloscope",
) -> go.Figure:
    """Build stacked interactive waveform subplots."""
    keys = selected_signals if selected_signals else list(signals.keys())
    style = THEMES.get(theme, THEMES["oscilloscope"])
    fig = make_subplots(rows=len(keys), cols=1, shared_xaxes=True, subplot_titles=keys)
    for i, name in enumerate(keys, start=1):
        values = signals[name]
        if values.ndim > 1:
            values = values[:, 0]
        fig.add_trace(go.Scatter(x=time, y=values, mode="lines", name=name), row=i, col=1)
        fig.update_yaxes(title_text=name, row=i, col=1)
    fig.update_layout(
        paper_bgcolor=style["paper_bgcolor"],
        plot_bgcolor=style["plot_bgcolor"],
        font=dict(color=style["font_color"]),
        height=max(350, 240 * len(keys)),
        hovermode="x unified",
        margin=dict(l=40, r=20, t=40, b=35),
    )
    fig.update_xaxes(showgrid=True, gridcolor=style["grid_color"], title_text="Time (s)")
    fig.update_yaxes(showgrid=True, gridcolor=style["grid_color"])
    return fig


def spectrum_figure(
    signal: np.ndarray,
    fs: float,
    fundamental_hz: float,
    odd_only: bool,
    theme: str = "oscilloscope",
) -> tuple[go.Figure, float]:
    """Build harmonic spectrum chart and return THD percentage."""
    style = THEMES.get(theme, THEMES["oscilloscope"])
    freqs, mags = compute_fft(signal, fs)
    max_order = 25
    orders = np.arange(1, max_order + 1)
    amps = []
    for k in orders:
        idx = int(np.argmin(np.abs(freqs - k * fundamental_hz)))
        amps.append(float(mags[idx]))
    orders = np.array(orders)
    amps = np.array(amps)
    if odd_only:
        mask = orders % 2 == 1
        orders = orders[mask]
        amps = amps[mask]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=orders, y=amps, marker_color=style["accent"], name="Harmonics"))
    fig.update_layout(
        paper_bgcolor=style["paper_bgcolor"],
        plot_bgcolor=style["plot_bgcolor"],
        font=dict(color=style["font_color"]),
        xaxis_title="Harmonic Order",
        yaxis_title="Amplitude (V)",
        margin=dict(l=40, r=20, t=40, b=35),
    )
    fig.update_xaxes(showgrid=True, gridcolor=style["grid_color"])
    fig.update_yaxes(showgrid=True, gridcolor=style["grid_color"])
    thd = compute_thd(signal, fundamental_hz, fs)
    return fig, thd
