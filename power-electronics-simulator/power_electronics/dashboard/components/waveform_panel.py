"""Oscilloscope-grade waveform display panel with signal selection, cursors,
measurement readout, and export-ready graph.
"""

from dash import dcc, html


def waveform_panel() -> html.Div:
    """Build waveform panel with signal selector, measurement bar, and graph area."""
    return html.Div(
        className="panel waveform-panel",
        children=[
            # ── Toolbar ────────────────────────────────────────────────
            html.Div(
                className="waveform-toolbar",
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "space-between",
                    "gap": "12px",
                    "padding": "6px 10px",
                    "borderBottom": "1px solid var(--grid-color, #1a3a2a)",
                    "flexWrap": "wrap",
                },
                children=[
                    html.Div(
                        style={"display": "flex", "alignItems": "center", "gap": "8px"},
                        children=[
                            html.Label(
                                "Signals:",
                                style={"fontSize": "11px", "fontWeight": "bold"},
                            ),
                            dcc.Checklist(
                                id="signal-selector",
                                inline=True,
                                style={"fontSize": "11px"},
                                inputStyle={"marginRight": "3px"},
                                labelStyle={"marginRight": "10px"},
                            ),
                        ],
                    ),
                    html.Div(
                        id="waveform-measurements",
                        style={
                            "display": "flex",
                            "gap": "14px",
                            "fontSize": "10px",
                            "fontFamily": "'JetBrains Mono', monospace",
                            "color": "var(--muted, #7a8ca5)",
                        },
                    ),
                ],
            ),
            # ── Graph ──────────────────────────────────────────────────
            dcc.Graph(
                id="waveform-graph",
                config={
                    "displaylogo": False,
                    "scrollZoom": True,
                    "modeBarButtonsToAdd": ["drawline", "drawrect", "eraseshape"],
                    "toImageButtonOptions": {
                        "format": "svg",
                        "filename": "waveform_export",
                        "height": 600,
                        "width": 1200,
                        "scale": 2,
                    },
                },
                style={"height": "calc(100% - 50px)"},
            ),
        ],
    )
