"""Dual-panel harmonic spectrum component with THD gauge, individual harmonic
distortion table, and configurable harmonic range.
"""

from dash import dcc, html


def spectrum_panel() -> html.Div:
    """Build harmonic spectrum panel with controls and dual-graph display."""
    return html.Div(
        className="panel spectrum-panel",
        children=[
            # ── Toolbar ────────────────────────────────────────────────
            html.Div(
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "space-between",
                    "gap": "10px",
                    "padding": "6px 10px",
                    "borderBottom": "1px solid var(--grid-color, #1a3a2a)",
                    "flexWrap": "wrap",
                },
                children=[
                    html.Div(
                        style={"display": "flex", "alignItems": "center", "gap": "12px"},
                        children=[
                            dcc.Checklist(
                                id="odd-only-toggle",
                                options=[{"label": " Odd Harmonics Only", "value": "odd"}],
                                value=[],
                                style={"fontSize": "11px"},
                                inputStyle={"marginRight": "4px"},
                            ),
                            html.Label(
                                "Max Order:",
                                style={"fontSize": "11px", "fontWeight": "bold"},
                            ),
                            dcc.Dropdown(
                                id="max-harmonic-order",
                                options=[
                                    {"label": "15", "value": 15},
                                    {"label": "25", "value": 25},
                                    {"label": "50", "value": 50},
                                ],
                                value=25,
                                clearable=False,
                                style={"width": "70px", "fontSize": "11px"},
                            ),
                        ],
                    ),
                    # THD readout
                    html.Div(
                        style={
                            "display": "flex",
                            "alignItems": "center",
                            "gap": "15px",
                        },
                        children=[
                            html.Div(
                                id="thd-display",
                                children="THD: -- %",
                                style={
                                    "fontSize": "14px",
                                    "fontWeight": "bold",
                                    "fontFamily": "'JetBrains Mono', monospace",
                                    "color": "var(--accent, #00ff88)",
                                },
                            ),
                            html.Div(
                                id="thd-r-display",
                                children="THD-R: -- %",
                                style={
                                    "fontSize": "11px",
                                    "fontFamily": "'JetBrains Mono', monospace",
                                    "color": "var(--muted, #7a8ca5)",
                                },
                            ),
                        ],
                    ),
                ],
            ),
            # ── Spectrum chart ─────────────────────────────────────────
            dcc.Graph(
                id="spectrum-graph",
                config={
                    "displaylogo": False,
                    "toImageButtonOptions": {
                        "format": "svg",
                        "filename": "spectrum_export",
                        "height": 400,
                        "width": 900,
                        "scale": 2,
                    },
                },
                style={"height": "340px"},
            ),
            # ── Individual harmonic distortion table ───────────────────
            html.Div(
                style={
                    "marginTop": "8px",
                    "padding": "8px",
                    "borderRadius": "6px",
                    "border": "1px solid var(--grid-color, #26344c)",
                    "background": "var(--bg-alt, #141925)",
                    "maxHeight": "140px",
                    "overflowY": "auto",
                },
                children=[
                    html.H4(
                        "Individual Harmonic Distortion",
                        style={"fontSize": "11px", "margin": "0 0 6px 0"},
                    ),
                    html.Div(
                        id="ihd-table",
                        style={
                            "display": "grid",
                            "gridTemplateColumns": "repeat(auto-fill, minmax(80px, 1fr))",
                            "gap": "4px",
                            "fontSize": "10px",
                            "fontFamily": "'JetBrains Mono', monospace",
                        },
                    ),
                ],
            ),
        ],
    )
