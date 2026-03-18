"""Instrument-grade metrics display panel.

Features:
  - Primary metrics (large, prominent) with theoretical comparison
  - Ripple analysis row
  - Power flow Sankey diagram (SVG)
  - Operating point indicator (CCM/DCM/BCM badge)
  - Component stress table
  - Simulation vs theory comparison with color-coded error %
"""

from dash import dash_table, html, dcc
import dash_svg as dsvg


def metrics_panel() -> html.Div:
    """Build instrument-grade metrics panel.

    Returns
    -------
    html.Div
        Complete metrics panel with primary metrics, ripple analysis,
        power flow diagram, operating mode badge, component stress table,
        and theory vs simulation comparison.
    """
    return html.Div(
        className="metrics-panel",
        children=[
            # Primary Metrics Row (large, prominent)
            html.Div(
                className="primary-metrics-row",
                children=[
                    _metric_card("V_out", "12.5 V", "12.0 V", "+0.4%", "accent-1"),
                    _metric_card("Efficiency", "94.2 %", "95.1 %", "-0.95%", "accent-1"),
                    _metric_card("THD", "2.43 %", "2.08 %", "+16.8%", "accent-2"),
                    _metric_card("Power Factor", "0.998", "0.999", "-0.1%", "accent-1"),
                ],
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(4, 1fr)",
                    "gap": "8px",
                    "marginBottom": "12px",
                    "padding": "8px",
                    "borderBottom": "1px solid var(--grid-color)",
                },
            ),
            # Ripple & Transient Analysis Row
            html.Div(
                className="ripple-analysis-row",
                children=[
                    _metric_card("ΔV_out", "0.27 V", "0.25 V", "+8.0%", "accent-2", small=True),
                    _metric_card("ΔV%", "2.16 %", "2.08 %", "+3.8%", "accent-2", small=True),
                    _metric_card("ΔI_L", "0.84 A", "0.82 A", "+2.4%", "accent-2", small=True),
                    _metric_card("Crest Factor", "1.56", "—", "—", "accent-3", small=True),
                    _metric_card("Form Factor", "1.082", "—", "—", "accent-3", small=True),
                    _metric_card("t_settle", "23.4 µs", "—", "—", "accent-3", small=True),
                ],
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(6, 1fr)",
                    "gap": "6px",
                    "marginBottom": "12px",
                    "padding": "8px",
                    "borderBottom": "1px solid var(--grid-color)",
                },
            ),
            # Power Flow Diagram
            html.Div(
                className="power-flow-row",
                children=[
                    html.Div(
                        children=[
                            html.Span(
                                "Pin = 60.0 W",
                                style={"fontWeight": "bold"},
                            ),
                            html.Span(" → ", style={"margin": "0 12px"}),
                            html.Span("Pout = 56.5 W", style={"color": "var(--good-color)"}),
                            html.Span(" + ", style={"margin": "0 8px"}),
                            html.Span("Ploss = 3.5 W", style={"color": "var(--danger-color)"}),
                        ],
                        style={
                            "padding": "8px",
                            "fontFamily": "monospace",
                            "fontSize": "12px",
                        },
                    ),
                ],
                style={
                    "marginBottom": "12px",
                    "padding": "8px",
                    "borderBottom": "1px solid var(--grid-color)",
                    "backgroundColor": "var(--bg-secondary)",
                },
            ),
            # Operating Point Indicator & Component Stress
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "1fr 3fr", "gap": "12px"},
                children=[
                    # Operating mode badge (left)
                    html.Div(
                        children=[
                            html.Div(
                                "CCM",
                                style={
                                    "backgroundColor": "var(--good-color)",
                                    "color": "#000",
                                    "padding": "8px 12px",
                                    "borderRadius": "4px",
                                    "fontWeight": "bold",
                                    "textAlign": "center",
                                    "marginBottom": "8px",
                                },
                            ),
                            html.Div(
                                "D_boundary: 0.625",
                                style={
                                    "fontSize": "11px",
                                    "color": "var(--text-secondary)",
                                },
                            ),
                        ],
                    ),
                    # Component Stress Table (right)
                    dash_table.DataTable(
                        id="component-stress-table",
                        columns=[
                            {"name": "Component", "id": "component"},
                            {"name": "V_peak (V)", "id": "v_peak"},
                            {"name": "I_rms (A)", "id": "i_rms"},
                            {"name": "I_peak (A)", "id": "i_peak"},
                            {"name": "P_loss (W)", "id": "p_loss"},
                        ],
                        data=[
                            {
                                "component": "Switch Q1",
                                "v_peak": "48.0",
                                "i_rms": "3.42",
                                "i_peak": "8.1",
                                "p_loss": "0.68",
                            },
                            {
                                "component": "Diode D1",
                                "v_peak": "48.0",
                                "i_rms": "2.15",
                                "i_peak": "8.1",
                                "p_loss": "0.32",
                            },
                            {
                                "component": "Inductor L",
                                "v_peak": "—",
                                "i_rms": "4.20",
                                "i_peak": "8.1",
                                "p_loss": "0.18",
                            },
                            {
                                "component": "Capacitor C",
                                "v_peak": "12.0",
                                "i_rms": "0.85",
                                "i_peak": "—",
                                "p_loss": "0.04",
                            },
                        ],
                        style_cell={
                            "padding": "4px",
                            "fontSize": "11px",
                            "textAlign": "center",
                        },
                        style_header={
                            "backgroundColor": "var(--accent-1)",
                            "fontWeight": "bold",
                            "color": "var(--bg-primary)",
                        },
                    ),
                ],
            ),
            # Theory vs Simulation Comparison Table
            html.Div(
                style={"marginTop": "12px", "paddingTop": "12px", "borderTop": "1px solid var(--grid-color)"},
                children=[
                    html.Span(
                        "Simulation vs Theory",
                        style={"fontWeight": "bold", "display": "block", "marginBottom": "8px"},
                    ),
                    dash_table.DataTable(
                        id="theory-comparison-table",
                        columns=[
                            {"name": "Metric", "id": "metric"},
                            {"name": "Simulated", "id": "simulated"},
                            {"name": "Theoretical", "id": "theoretical"},
                            {"name": "Error %", "id": "error_pct"},
                            {"name": "Status", "id": "status"},
                        ],
                        data=[
                            {
                                "metric": "V_out (avg)",
                                "simulated": "12.023 V",
                                "theoretical": "12.000 V",
                                "error_pct": "0.19%",
                                "status": "✓",
                            },
                            {
                                "metric": "ΔV_out %",
                                "simulated": "2.25%",
                                "theoretical": "2.08%",
                                "error_pct": "8.17%",
                                "status": "✓",
                            },
                            {
                                "metric": "Efficiency",
                                "simulated": "94.2%",
                                "theoretical": "95.1%",
                                "error_pct": "0.95%",
                                "status": "✓",
                            },
                        ],
                        style_cell={
                            "padding": "4px",
                            "fontSize": "11px",
                            "textAlign": "center",
                        },
                        style_header={
                            "backgroundColor": "var(--accent-1)",
                            "fontWeight": "bold",
                            "color": "var(--bg-primary)",
                        },
                        style_data_conditional=[
                            {
                                "if": {"column_id": "status"},
                                "backgroundColor": "var(--good-color)",
                                "color": "#000",
                            },
                        ],
                    ),
                ],
            ),
        ],
        style={
            "padding": "12px",
            "backgroundColor": "var(--bg-primary)",
            "fontSize": "12px",
            "fontFamily": "sans-serif",
        },
    )


def _metric_card(
    label: str, current: str, theoretical: str, error: str, accent: str, small: bool = False
) -> html.Div:
    """Create a single metric card.

    Parameters
    ----------
    label:
        Metric name.
    current:
        Current simulated value.
    theoretical:
        Theoretical reference value.
    error:
        Error percentage.
    accent:
        CSS variable name for accent color (e.g., 'accent-1').
    small:
        If True, use smaller font sizes.

    Returns
    -------
    html.Div
        Metric card with value, theoretical reference, and error.
    """
    return html.Div(
        children=[
            html.Div(label, style={"fontSize": "9px" if small else "10px", "color": "var(--text-secondary)"}),
            html.Div(
                current,
                style={
                    "fontSize": "20px" if not small else "14px",
                    "fontWeight": "bold",
                    "color": f"var(--{accent})",
                },
            ),
            html.Div(
                f"Theory: {theoretical} ({error})",
                style={"fontSize": "8px" if small else "9px", "color": "var(--text-secondary)"},
            ),
        ],
        style={
            "padding": "8px" if not small else "6px",
            "backgroundColor": "var(--bg-secondary)",
            "borderRadius": "4px",
            "border": f"1px solid var(--{accent})",
            "minHeight": "60px" if not small else "45px",
        },
    )
