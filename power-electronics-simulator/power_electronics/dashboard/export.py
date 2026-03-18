"""Export utilities for simulation results (PNG, SVG, CSV, JSON, PDF).

Supports exporting simulation results in multiple formats for further analysis,
publication, or sharing with colleagues.
"""

from __future__ import annotations

import base64
import io
import json
from datetime import datetime
from typing import Any

import numpy as np
import plotly.graph_objects as go
from plotly.io import to_image, to_json
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageTemplate,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    Paragraph,
    Image,
    KeepTogether,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from power_electronics.core.base_converter import SimulationResult


# ==============================================================================
# PLOTLY FIGURE EXPORT
# ==============================================================================


def export_png(
    figure: go.Figure, filename: str | None = None, scale: int = 3
) -> bytes:
    """Export Plotly figure to PNG format.

    Parameters
    ----------
    figure:
        Plotly Figure object.
    filename:
        Optional output filename. If None, returns bytes.
    scale:
        Pixel scale factor (default 3 for high quality).

    Returns
    -------
    bytes
        PNG image bytes.
    """
    try:
        png_bytes = to_image(figure, format="png", scale=scale, width=1200, height=600)
        if filename:
            with open(filename, "wb") as f:
                f.write(png_bytes)
        return png_bytes
    except Exception as e:
        raise IOError(f"Failed to export PNG: {e}") from e


def export_svg(figure: go.Figure, filename: str | None = None) -> bytes:
    """Export Plotly figure to SVG format.

    Parameters
    ----------
    figure:
        Plotly Figure object.
    filename:
        Optional output filename. If None, returns bytes.

    Returns
    -------
    bytes
        SVG image bytes.
    """
    try:
        svg_bytes = to_image(figure, format="svg", width=1200, height=600)
        if filename:
            with open(filename, "wb") as f:
                f.write(svg_bytes)
        return svg_bytes
    except Exception as e:
        raise IOError(f"Failed to export SVG: {e}") from e


# ==============================================================================
# DATA EXPORT (CSV, JSON)
# ==============================================================================


def export_csv(result: SimulationResult, filename: str | None = None) -> bytes:
    """Export simulation result to CSV format.

    Time-domain data with all signals as columns. Includes header row with units.

    Parameters
    ----------
    result:
        SimulationResult object.
    filename:
        Optional output filename. If None, returns bytes.

    Returns
    -------
    bytes
        CSV data as bytes (UTF-8).
    """
    lines: list[str] = []

    # Header: signal names
    header_names = ["Time (s)"] + list(result.signals.keys())
    lines.append(",".join(header_names))

    # Data rows
    n_samples = len(result.time)
    for i in range(n_samples):
        row_values = [str(result.time[i])]
        for signal_name in result.signals.keys():
            row_values.append(str(result.signals[signal_name][i]))
        lines.append(",".join(row_values))

    csv_text = "\n".join(lines)
    csv_bytes = csv_text.encode("utf-8")

    if filename:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(csv_text)

    return csv_bytes


def export_json(result: SimulationResult, filename: str | None = None) -> bytes:
    """Export full SimulationResult to JSON format.

    Parameters
    ----------
    result:
        SimulationResult object.
    filename:
        Optional output filename. If None, returns bytes.

    Returns
    -------
    bytes
        JSON data as bytes (UTF-8).
    """
    data: dict[str, Any] = {
        "converter_name": result.converter_name,
        "timestamp": datetime.now().isoformat(),
        "version": "0.2.0",
        "parameters": result.params,
        "metrics": result.metrics,
        "time": result.time.tolist(),
        "signals": {
            name: signal.tolist() for name, signal in result.signals.items()
        },
    }

    json_str = json.dumps(data, indent=2)
    json_bytes = json_str.encode("utf-8")

    if filename:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(json_str)

    return json_bytes


# ==============================================================================
# PDF REPORT GENERATION
# ==============================================================================


def export_report_pdf(
    result: SimulationResult,
    waveform_figure: go.Figure | None = None,
    spectrum_figure: go.Figure | None = None,
    filename: str | None = None,
) -> bytes:
    """Generate professional PDF report from simulation result.

    Report includes:
      - Converter name and parameters table
      - Waveform plot
      - Metrics table
      - Harmonic spectrum
      - Simulation settings
      - Footer with timestamp and version

    Parameters
    ----------
    result:
        SimulationResult object.
    waveform_figure:
        Optional Plotly waveform figure to include.
    spectrum_figure:
        Optional Plotly spectrum figure to include.
    filename:
        Optional output filename. If None, returns bytes.

    Returns
    -------
    bytes
        PDF data as bytes.
    """
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter,
        rightMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        textColor=colors.HexColor("#1565c0"),
        spaceAfter=6,
        alignment=TA_CENTER,
    )
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#1565c0"),
        spaceAfter=8,
        spaceBefore=12,
    )

    story: list[Any] = []

    # Title
    title = Paragraph(
        f"Power Converter Analysis Report: {result.converter_name}",
        title_style,
    )
    story.append(title)
    story.append(Spacer(1, 0.2 * inch))

    # Parameters Table
    story.append(Paragraph("Simulation Parameters", heading_style))
    param_data = [["Parameter", "Value"]]
    for key, val in result.params.items():
        param_data.append([str(key), str(val)])

    param_table = Table(param_data, colWidths=[2.5 * inch, 2.5 * inch])
    param_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1565c0")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 11),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.grey),
            ]
        )
    )
    story.append(param_table)
    story.append(Spacer(1, 0.2 * inch))

    # Metrics Table
    story.append(Paragraph("Simulation Metrics", heading_style))
    metric_data = [["Metric", "Value"]]
    for key, val in result.metrics.items():
        if isinstance(val, float):
            metric_data.append([str(key), f"{val:.4f}"])
        else:
            metric_data.append([str(key), str(val)])

    metric_table = Table(metric_data, colWidths=[2.5 * inch, 2.5 * inch])
    metric_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#c62828")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 11),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("BACKGROUND", (0, 1), (-1, -1), colors.lightblue),
                ("GRID", (0, 0), (-1, -1), 1, colors.grey),
            ]
        )
    )
    story.append(metric_table)
    story.append(Spacer(1, 0.2 * inch))

    # Waveform Plot (if provided)
    if waveform_figure is not None:
        try:
            story.append(Paragraph("Waveforms", heading_style))
            png_bytes = export_png(waveform_figure)
            img_buffer = io.BytesIO(png_bytes)
            img = Image(img_buffer, width=5.5 * inch, height=2.5 * inch)
            story.append(img)
            story.append(Spacer(1, 0.2 * inch))
        except Exception:
            pass  # Silently skip if image generation fails

    # Spectrum Plot (if provided)
    if spectrum_figure is not None:
        try:
            story.append(Paragraph("Harmonic Spectrum", heading_style))
            png_bytes = export_png(spectrum_figure)
            img_buffer = io.BytesIO(png_bytes)
            img = Image(img_buffer, width=5.5 * inch, height=2.5 * inch)
            story.append(img)
            story.append(Spacer(1, 0.2 * inch))
        except Exception:
            pass  # Silently skip if image generation fails

    # Footer
    story.append(Spacer(1, 0.3 * inch))
    footer_text = (
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} "
        "| Power Electronics Simulator v0.2.0"
    )
    footer = Paragraph(footer_text, ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER,
    ))
    story.append(footer)

    # Build PDF
    doc.build(story)
    pdf_bytes = pdf_buffer.getvalue()

    if filename:
        with open(filename, "wb") as f:
            f.write(pdf_bytes)

    return pdf_bytes


# ==============================================================================
# BATCH EXPORT UTILITIES
# ==============================================================================


def export_all_formats(
    result: SimulationResult,
    output_dir: str,
    waveform_figure: go.Figure | None = None,
    spectrum_figure: go.Figure | None = None,
) -> dict[str, str]:
    """Export simulation result in all formats to directory.

    Parameters
    ----------
    result:
        SimulationResult object.
    output_dir:
        Directory to save files to.
    waveform_figure:
        Optional waveform Plotly figure.
    spectrum_figure:
        Optional spectrum Plotly figure.

    Returns
    -------
    dict[str, str]
        Mapping of format → output filename.
    """
    import os

    os.makedirs(output_dir, exist_ok=True)

    base_name = result.converter_name.replace(" ", "_").lower()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = f"{base_name}_{timestamp}"

    outputs: dict[str, str] = {}

    # CSV
    csv_file = os.path.join(output_dir, f"{prefix}.csv")
    export_csv(result, csv_file)
    outputs["csv"] = csv_file

    # JSON
    json_file = os.path.join(output_dir, f"{prefix}.json")
    export_json(result, json_file)
    outputs["json"] = json_file

    # PNG (if waveform figure provided)
    if waveform_figure is not None:
        try:
            png_file = os.path.join(output_dir, f"{prefix}_waveform.png")
            export_png(waveform_figure, png_file)
            outputs["png"] = png_file
        except Exception:
            pass

    # SVG (if waveform figure provided)
    if waveform_figure is not None:
        try:
            svg_file = os.path.join(output_dir, f"{prefix}_waveform.svg")
            export_svg(waveform_figure, svg_file)
            outputs["svg"] = svg_file
        except Exception:
            pass

    # PDF Report
    try:
        pdf_file = os.path.join(output_dir, f"{prefix}_report.pdf")
        export_report_pdf(result, waveform_figure, spectrum_figure, pdf_file)
        outputs["pdf"] = pdf_file
    except Exception:
        pass

    return outputs
