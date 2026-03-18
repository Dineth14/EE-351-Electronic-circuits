"""Plotly-based interactive chart generation with oscilloscope-grade styling.

Provides publication-quality waveform figures, harmonic spectrum charts,
efficiency surface plots, Bode diagrams, and transient response overlays.
"""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from power_electronics.core.analysis import (
    compute_fft,
    compute_harmonic_spectrum,
    compute_rms,
    compute_thd,
)
from power_electronics.visualization.themes import THEMES, get_theme, get_trace_color


# ---------------------------------------------------------------------------
# Waveform Figure
# ---------------------------------------------------------------------------

def build_waveform_figure(
    time: np.ndarray,
    signals: dict[str, np.ndarray],
    selected_signals: list[str] | None = None,
    theme: str = "oscilloscope",
) -> go.Figure:
    """Build stacked oscilloscope-style waveform subplots.

    Each selected signal gets its own subplot with individual Y-axis,
    shared X-axis, crosshair cursor, and themed coloring.
    """
    th = get_theme(theme)
    style = THEMES.get(theme, THEMES["oscilloscope"])
    keys = selected_signals if selected_signals else list(signals.keys())
    if not keys:
        keys = list(signals.keys())[:4]
    n_rows = len(keys)

    fig = make_subplots(
        rows=n_rows, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=keys,
    )

    for i, name in enumerate(keys, start=1):
        values = signals.get(name, np.zeros_like(time))
        if values.ndim > 1:
            values = values[:, 0]
        color = get_trace_color(th, i - 1)

        fig.add_trace(
            go.Scattergl(
                x=time, y=values,
                mode="lines",
                name=name,
                line=dict(color=color, width=th.layout.line_width),
                hovertemplate=f"<b>{name}</b><br>t=%{{x:.6f}}s<br>val=%{{y:.4f}}<extra></extra>",
            ),
            row=i, col=1,
        )

        rms_val = compute_rms(values)
        mean_val = float(np.mean(values))
        fig.add_hline(
            y=mean_val, row=i, col=1,
            line=dict(color=th.colors.text_secondary, width=0.8, dash="dash"),
            annotation_text=f"DC={mean_val:.3f}",
            annotation_font_size=9,
            annotation_font_color=th.colors.text_secondary,
        )

        fig.update_yaxes(
            title_text=name, row=i, col=1,
            title_font_size=th.typography.size_axis,
            tickfont_size=th.typography.size_tick,
        )

    fig.update_layout(
        paper_bgcolor=style["paper_bgcolor"],
        plot_bgcolor=style["plot_bgcolor"],
        font=dict(color=style["font_color"], family=th.typography.family),
        height=max(350, 220 * n_rows),
        hovermode="x unified",
        margin=th.layout.margin,
        showlegend=False,
        title=dict(
            text="Signal Waveforms",
            font_size=th.typography.size_title,
            x=0.02,
        ),
    )
    fig.update_xaxes(
        showgrid=True, gridcolor=style["grid_color"],
        gridwidth=th.layout.grid_width, griddash=th.layout.grid_dash,
        title_text="Time (s)",
        tickfont_size=th.typography.size_tick,
        spikemode="across", spikethickness=1,
        spikecolor=th.colors.accent, spikedash="solid",
    )
    fig.update_yaxes(
        showgrid=True, gridcolor=style["grid_color"],
        gridwidth=th.layout.grid_width, griddash=th.layout.grid_dash,
        tickfont_size=th.typography.size_tick,
    )
    return fig


# ---------------------------------------------------------------------------
# Spectrum Figure
# ---------------------------------------------------------------------------

def spectrum_figure(
    signal: np.ndarray,
    fs: float,
    fundamental_hz: float,
    odd_only: bool,
    theme: str = "oscilloscope",
) -> tuple[go.Figure, float]:
    """Build harmonic spectrum bar chart with fundamental highlight and THD annotation."""
    th = get_theme(theme)
    style = THEMES.get(theme, THEMES["oscilloscope"])

    max_order = 25
    orders, amps = compute_harmonic_spectrum(signal, fundamental_hz, fs, max_order)

    if odd_only:
        mask = orders % 2 == 1
        orders = orders[mask]
        amps = amps[mask]

    fund_amp = amps[0] if len(amps) > 0 else 0.0
    colors = [
        th.colors.accent if (k == 1) else th.colors.accent_secondary
        for k in orders
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=orders, y=amps,
        marker_color=colors,
        marker_line_width=0,
        opacity=th.layout.bar_opacity,
        name="Harmonics",
        hovertemplate="Order %{x}<br>Amplitude: %{y:.4f} V<extra></extra>",
    ))

    thd = compute_thd(signal, fundamental_hz, fs)

    fig.add_annotation(
        x=0.98, y=0.95, xref="paper", yref="paper",
        text=f"<b>THD = {thd:.2f}%</b><br>f₁ = {fundamental_hz:.1f} Hz<br>V₁ = {fund_amp:.3f} V",
        showarrow=False,
        font=dict(size=12, color=th.colors.accent),
        bgcolor=style["paper_bgcolor"],
        bordercolor=th.colors.border_color,
        borderwidth=1, borderpad=6,
        xanchor="right",
    )

    fig.update_layout(
        paper_bgcolor=style["paper_bgcolor"],
        plot_bgcolor=style["plot_bgcolor"],
        font=dict(color=style["font_color"], family=th.typography.family),
        xaxis_title="Harmonic Order",
        yaxis_title="Amplitude (V)",
        margin=th.layout.margin,
        title=dict(text="Harmonic Spectrum", font_size=th.typography.size_title, x=0.02),
        bargap=0.15,
    )
    fig.update_xaxes(
        showgrid=True, gridcolor=style["grid_color"],
        gridwidth=th.layout.grid_width, dtick=1,
    )
    fig.update_yaxes(
        showgrid=True, gridcolor=style["grid_color"],
        gridwidth=th.layout.grid_width, griddash=th.layout.grid_dash,
    )
    return fig, thd


# ---------------------------------------------------------------------------
# Efficiency Map
# ---------------------------------------------------------------------------

def build_efficiency_map(
    duty_cycles: np.ndarray,
    load_fractions: np.ndarray,
    efficiency_grid: np.ndarray,
    theme: str = "oscilloscope",
) -> go.Figure:
    """Build 2-D efficiency heatmap over duty cycle × load fraction."""
    th = get_theme(theme)
    style = THEMES.get(theme, THEMES["oscilloscope"])

    fig = go.Figure(data=go.Heatmap(
        z=efficiency_grid,
        x=duty_cycles,
        y=load_fractions,
        colorscale="Viridis",
        colorbar=dict(title="η (%)"),
        hovertemplate="D=%{x:.2f}<br>Load=%{y:.1f}%<br>η=%{z:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor=style["paper_bgcolor"],
        plot_bgcolor=style["plot_bgcolor"],
        font=dict(color=style["font_color"], family=th.typography.family),
        title=dict(text="Efficiency Map", font_size=th.typography.size_title, x=0.02),
        xaxis_title="Duty Cycle",
        yaxis_title="Load Fraction (%)",
        margin=th.layout.margin,
    )
    return fig


# ---------------------------------------------------------------------------
# Bode Plot
# ---------------------------------------------------------------------------

def build_bode_figure(
    freqs: np.ndarray,
    mag_db: np.ndarray,
    phase_deg: np.ndarray,
    theme: str = "oscilloscope",
) -> go.Figure:
    """Build dual-subplot Bode magnitude/phase plot."""
    th = get_theme(theme)
    style = THEMES.get(theme, THEMES["oscilloscope"])

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=["Magnitude (dB)", "Phase (°)"],
    )
    fig.add_trace(
        go.Scattergl(
            x=freqs, y=mag_db, mode="lines",
            line=dict(color=th.colors.accent, width=th.layout.line_width),
            name="Magnitude",
        ),
        row=1, col=1,
    )
    fig.add_trace(
        go.Scattergl(
            x=freqs, y=phase_deg, mode="lines",
            line=dict(color=th.colors.accent_secondary, width=th.layout.line_width),
            name="Phase",
        ),
        row=2, col=1,
    )

    # 0 dB and -180° reference lines
    fig.add_hline(y=0, row=1, col=1, line=dict(color=th.colors.text_secondary, width=0.7, dash="dash"))
    fig.add_hline(y=-180, row=2, col=1, line=dict(color=th.colors.danger, width=0.7, dash="dash"))

    fig.update_xaxes(type="log", title_text="Frequency (Hz)", row=2, col=1)
    fig.update_xaxes(type="log", row=1, col=1)
    fig.update_yaxes(title_text="dB", row=1, col=1)
    fig.update_yaxes(title_text="°", row=2, col=1)

    fig.update_layout(
        paper_bgcolor=style["paper_bgcolor"],
        plot_bgcolor=style["plot_bgcolor"],
        font=dict(color=style["font_color"], family=th.typography.family),
        height=500,
        margin=th.layout.margin,
        showlegend=False,
        title=dict(text="Bode Plot", font_size=th.typography.size_title, x=0.02),
    )
    fig.update_xaxes(showgrid=True, gridcolor=style["grid_color"], gridwidth=th.layout.grid_width)
    fig.update_yaxes(showgrid=True, gridcolor=style["grid_color"], gridwidth=th.layout.grid_width)
    return fig


# ---------------------------------------------------------------------------
# Transient Comparison
# ---------------------------------------------------------------------------

def build_transient_comparison(
    results: list[dict],
    theme: str = "oscilloscope",
) -> go.Figure:
    """Overlay transient responses from multiple simulation runs.

    Parameters
    ----------
    results : list[dict]
        Each dict has keys: 'label', 'time', 'signal'.
    """
    th = get_theme(theme)
    style = THEMES.get(theme, THEMES["oscilloscope"])

    fig = go.Figure()
    for i, r in enumerate(results):
        fig.add_trace(go.Scattergl(
            x=r["time"], y=r["signal"],
            mode="lines",
            name=r.get("label", f"Run {i + 1}"),
            line=dict(color=get_trace_color(th, i), width=th.layout.line_width),
        ))

    fig.update_layout(
        paper_bgcolor=style["paper_bgcolor"],
        plot_bgcolor=style["plot_bgcolor"],
        font=dict(color=style["font_color"], family=th.typography.family),
        title=dict(text="Transient Response Comparison", font_size=th.typography.size_title, x=0.02),
        xaxis_title="Time (s)",
        yaxis_title="Amplitude",
        margin=th.layout.margin,
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(0,0,0,0.5)"),
    )
    fig.update_xaxes(showgrid=True, gridcolor=style["grid_color"], gridwidth=th.layout.grid_width)
    fig.update_yaxes(showgrid=True, gridcolor=style["grid_color"], gridwidth=th.layout.grid_width)
    return fig
