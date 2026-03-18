"""Theory & equations panel with LaTeX rendering, circuit description,
design equations, and CCM/DCM boundary information.
"""

from dash import dcc, html


def theory_panel() -> html.Div:
    """Build theory panel with equations, circuit diagram, and design info."""
    return html.Div(
        id="theory-panel",
        className="panel theory-panel",
        children=[
            # ── Converter Info Header ──────────────────────────────────
            html.Div(
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "flex-start",
                    "gap": "12px",
                    "flexWrap": "wrap",
                },
                children=[
                    html.Div(
                        style={"flex": "1", "minWidth": "250px"},
                        children=[
                            html.H3(
                                id="theory-title",
                                style={"margin": "0 0 6px 0", "fontSize": "16px"},
                            ),
                            html.P(
                                id="theory-description",
                                style={
                                    "fontSize": "12px",
                                    "color": "var(--muted, #7a8ca5)",
                                    "margin": "0 0 10px 0",
                                    "lineHeight": "1.5",
                                },
                            ),
                        ],
                    ),
                    html.Div(
                        id="theory-category-badge",
                        style={
                            "padding": "4px 12px",
                            "borderRadius": "4px",
                            "border": "1px solid var(--accent, #00ff88)",
                            "fontSize": "11px",
                            "fontWeight": "bold",
                            "color": "var(--accent, #00ff88)",
                            "whiteSpace": "nowrap",
                        },
                    ),
                ],
            ),
            # ── Key Equations ──────────────────────────────────────────
            html.Div(
                style={
                    "marginTop": "12px",
                    "padding": "10px",
                    "borderRadius": "6px",
                    "border": "1px solid var(--grid-color, #26344c)",
                    "background": "var(--bg-alt, #141925)",
                },
                children=[
                    html.H4(
                        "Key Equations",
                        style={"fontSize": "12px", "margin": "0 0 8px 0"},
                    ),
                    html.Div(id="theory-equations"),
                ],
            ),
            # ── Circuit Operating Diagram ──────────────────────────────
            html.Div(
                style={
                    "marginTop": "10px",
                    "padding": "10px",
                    "borderRadius": "6px",
                    "border": "1px solid var(--grid-color, #26344c)",
                    "background": "var(--bg-alt, #141925)",
                },
                children=[
                    html.H4(
                        "Operating Waveform",
                        style={"fontSize": "12px", "margin": "0 0 8px 0"},
                    ),
                    html.Img(
                        id="theory-circuit-img",
                        style={
                            "maxWidth": "100%",
                            "maxHeight": "220px",
                            "border": "1px solid var(--grid-color, #26344c)",
                            "borderRadius": "4px",
                        },
                    ),
                ],
            ),
            # ── Theoretical vs Simulated Values ────────────────────────
            html.Div(
                style={
                    "marginTop": "10px",
                    "padding": "10px",
                    "borderRadius": "6px",
                    "border": "1px solid var(--grid-color, #26344c)",
                    "background": "var(--bg-alt, #141925)",
                },
                children=[
                    html.H4(
                        "Theoretical Reference Values",
                        style={"fontSize": "12px", "margin": "0 0 8px 0"},
                    ),
                    html.Div(
                        id="theory-reference-values",
                        style={
                            "display": "grid",
                            "gridTemplateColumns": "repeat(auto-fill, minmax(150px, 1fr))",
                            "gap": "6px",
                            "fontSize": "11px",
                            "fontFamily": "'JetBrains Mono', monospace",
                        },
                    ),
                ],
            ),
            # ── CCM/DCM Boundary ───────────────────────────────────────
            html.Div(
                style={
                    "marginTop": "10px",
                    "padding": "10px",
                    "borderRadius": "6px",
                    "border": "1px solid var(--grid-color, #26344c)",
                    "background": "var(--bg-alt, #141925)",
                },
                children=[
                    html.H4(
                        "Operating Mode & Boundary",
                        style={"fontSize": "12px", "margin": "0 0 8px 0"},
                    ),
                    html.Div(id="theory-boundary-info"),
                ],
            ),
        ],
    )
