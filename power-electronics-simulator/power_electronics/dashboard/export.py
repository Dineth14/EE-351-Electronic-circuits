"""Export system for simulation results in multiple formats.

Supports CSV, JSON, PNG, SVG, and PDF export of waveforms, metrics,
and complete simulation reports.
"""

from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


# ---------------------------------------------------------------------------
# CSV Export
# ---------------------------------------------------------------------------

def export_csv(
    time: np.ndarray,
    signals: dict[str, np.ndarray],
    metrics: dict[str, float],
    converter_name: str,
) -> str:
    """Export simulation waveforms and metrics as CSV text.

    Returns
    -------
    str
        CSV-formatted string ready for download.
    """
    buf = io.StringIO()
    writer = csv.writer(buf)

    # Header: metadata comment
    writer.writerow([f"# Converter: {converter_name}"])
    writer.writerow([f"# Exported: {datetime.now(timezone.utc).isoformat()}"])
    writer.writerow([])

    # Metrics section
    writer.writerow(["# Metrics"])
    writer.writerow(["Metric", "Value"])
    for k, v in metrics.items():
        writer.writerow([k, f"{v:.6g}"])
    writer.writerow([])

    # Waveform section
    sig_names = list(signals.keys())
    writer.writerow(["# Waveforms"])
    writer.writerow(["time_s"] + sig_names)
    for i in range(len(time)):
        row = [f"{time[i]:.9g}"]
        for name in sig_names:
            val = signals[name]
            if val.ndim > 1:
                val = val[:, 0]
            row.append(f"{val[i]:.9g}")
        writer.writerow(row)

    return buf.getvalue()


# ---------------------------------------------------------------------------
# JSON Export
# ---------------------------------------------------------------------------

def export_json(
    time: np.ndarray,
    signals: dict[str, np.ndarray],
    metrics: dict[str, float],
    converter_name: str,
    params: dict,
) -> str:
    """Export complete simulation data as JSON.

    Returns
    -------
    str
        JSON string with metadata, parameters, metrics, and sampled waveforms.
    """
    # Downsample to max 2000 points for JSON size
    n = len(time)
    stride = max(1, n // 2000)

    payload = {
        "metadata": {
            "converter": converter_name,
            "exported": datetime.now(timezone.utc).isoformat(),
            "samples": n,
            "exported_samples": len(time[::stride]),
        },
        "parameters": {k: _serialize(v) for k, v in params.items()},
        "metrics": {k: round(v, 6) for k, v in metrics.items()},
        "waveforms": {
            "time_s": time[::stride].tolist(),
            **{
                name: (val[:, 0] if val.ndim > 1 else val)[::stride].tolist()
                for name, val in signals.items()
            },
        },
    }
    return json.dumps(payload, indent=2)


def _serialize(v):
    """Convert numpy scalars and arrays for JSON."""
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, np.ndarray):
        return v.tolist()
    return v


# ---------------------------------------------------------------------------
# PNG / SVG Figure Export
# ---------------------------------------------------------------------------

def export_figure_bytes(
    time: np.ndarray,
    signals: dict[str, np.ndarray],
    selected_signals: list[str] | None = None,
    fmt: str = "png",
    dpi: int = 150,
    title: str = "Simulation Waveforms",
) -> bytes:
    """Render matplotlib figure to bytes in PNG or SVG format.

    Parameters
    ----------
    time : np.ndarray
        Time vector.
    signals : dict[str, np.ndarray]
        Signal dictionary.
    selected_signals : list[str] or None
        Signals to include. None = all.
    fmt : str
        'png' or 'svg'.
    dpi : int
        DPI for raster export.
    title : str
        Figure title.

    Returns
    -------
    bytes
        Image data.
    """
    names = selected_signals or list(signals.keys())
    n = len(names)
    fig, axes = plt.subplots(n, 1, figsize=(12, max(3, 2.0 * n)), sharex=True)
    if n == 1:
        axes = [axes]

    colors = ["#00ff88", "#00ccff", "#ff6b9d", "#ffd700", "#a78bfa",
              "#fb923c", "#34d399", "#f472b6", "#60a5fa", "#facc15"]

    for i, (ax, name) in enumerate(zip(axes, names)):
        val = signals.get(name, np.zeros_like(time))
        if val.ndim > 1:
            val = val[:, 0]
        ax.plot(time, val, linewidth=1.2, color=colors[i % len(colors)])
        ax.set_ylabel(name, fontsize=10)
        ax.grid(True, alpha=0.3, linestyle=":")
        ax.tick_params(labelsize=9)

    axes[0].set_title(title, fontsize=13, fontweight="bold")
    axes[-1].set_xlabel("Time (s)", fontsize=10)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format=fmt, dpi=dpi, bbox_inches="tight",
                facecolor="#0a0a0f", edgecolor="none")
    plt.close(fig)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# PDF Report (text-based, no reportlab dependency required)
# ---------------------------------------------------------------------------

def export_pdf_report(
    time: np.ndarray,
    signals: dict[str, np.ndarray],
    metrics: dict[str, float],
    converter_name: str,
    params: dict,
    selected_signals: list[str] | None = None,
) -> bytes:
    """Generate a multi-page PDF report with waveforms and metrics.

    Uses matplotlib's PdfPages backend for reliable PDF generation
    without external dependencies beyond matplotlib.

    Returns
    -------
    bytes
        PDF file data.
    """
    from matplotlib.backends.backend_pdf import PdfPages

    buf = io.BytesIO()
    with PdfPages(buf) as pdf:
        # Page 1: Title & Metrics
        fig1, ax1 = plt.subplots(figsize=(8.5, 11))
        ax1.axis("off")
        y = 0.95
        ax1.text(0.5, y, "Power Electronics Simulation Report",
                 ha="center", fontsize=18, fontweight="bold", transform=ax1.transAxes)
        y -= 0.05
        ax1.text(0.5, y, f"Converter: {converter_name}",
                 ha="center", fontsize=14, transform=ax1.transAxes)
        y -= 0.03
        ax1.text(0.5, y, f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
                 ha="center", fontsize=10, color="gray", transform=ax1.transAxes)

        # Parameters
        y -= 0.06
        ax1.text(0.1, y, "Simulation Parameters:", fontsize=12,
                 fontweight="bold", transform=ax1.transAxes)
        for k, v in params.items():
            y -= 0.025
            if y < 0.05:
                break
            ax1.text(0.12, y, f"{k}: {v}", fontsize=9, transform=ax1.transAxes,
                     fontfamily="monospace")

        # Metrics
        y -= 0.04
        ax1.text(0.1, y, "Results:", fontsize=12,
                 fontweight="bold", transform=ax1.transAxes)
        for k, v in metrics.items():
            y -= 0.025
            if y < 0.05:
                break
            ax1.text(0.12, y, f"{k}: {v:.4g}", fontsize=9, transform=ax1.transAxes,
                     fontfamily="monospace")

        fig1.tight_layout()
        pdf.savefig(fig1, facecolor="white")
        plt.close(fig1)

        # Page 2: Waveforms
        names = selected_signals or list(signals.keys())[:6]
        n = len(names)
        fig2, axes = plt.subplots(n, 1, figsize=(8.5, max(5, 1.8 * n)), sharex=True)
        if n == 1:
            axes = [axes]
        for ax, name in zip(axes, names):
            val = signals.get(name, np.zeros_like(time))
            if val.ndim > 1:
                val = val[:, 0]
            ax.plot(time, val, linewidth=0.8)
            ax.set_ylabel(name, fontsize=9)
            ax.grid(True, alpha=0.3, linestyle=":")
            ax.tick_params(labelsize=8)
        axes[0].set_title(f"{converter_name} — Waveforms", fontsize=12)
        axes[-1].set_xlabel("Time (s)", fontsize=9)
        fig2.tight_layout()
        pdf.savefig(fig2, facecolor="white")
        plt.close(fig2)

    return buf.getvalue()
