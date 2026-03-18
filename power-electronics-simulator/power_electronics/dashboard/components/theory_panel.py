"""Theory tab panel with circuit diagrams, equations, and educational content.

Features:
  - Circuit schematic (rendered via schemdraw → PNG)
  - LaTeX equations with derivations (expandable)
  - Key waveform sketches (textbook quality)
  - Theoretical formulas with numerical substitution
  - Operating region charts (CCM/DCM for DC-DC, alpha for rectifiers, ma for inverters)
"""

from dash import dcc, html


def theory_panel() -> html.Div:
    """Build comprehensive theory education panel.

    Returns
    -------
    html.Div
        Theory tab with schematic, equations, waveform sketches, and operating regions.
    """
    return html.Div(
        className="theory-panel",
        children=[
            # Converter-specific header
            html.Div(
                style={
                    "padding": "12px",
                    "backgroundColor": "var(--bg-secondary)",
                    "borderBottom": "1px solid var(--grid-color)",
                    "marginBottom": "8px",
                },
                children=[
                    html.H2(id="theory-title", children="Buck Converter Theory"),
                    html.Span(
                        id="theory-description",
                        children="Step-down topology with PWM gating",
                        style={"color": "var(--text-secondary)", "fontSize": "12px"},
                    ),
                ],
            ),
            # Circuit schematic image (rendered from schemdraw)
            html.Div(
                style={"padding": "12px", "borderBottom": "1px solid var(--grid-color)"},
                children=[
                    html.H3("Circuit Topology", style={"marginTop": "0"}),
                    html.Div(
                        style={
                            "display": "flex",
                            "justifyContent": "space-around",
                            "alignItems": "center",
                            "gap": "16px",
                            "marginTop": "8px",
                        },
                        children=[
                            html.Div(
                                children=[
                                    html.Span(
                                        "ON State (Q conducting)",
                                        style={"fontWeight": "bold", "fontSize": "11px", "display": "block", "marginBottom": "4px"},
                                    ),
                                    html.Img(
                                        id="circuit-on-diagram",
                                        src="data:image/png;base64,",
                                        style={"height": "150px", "borderRadius": "4px"},
                                    ),
                                ],
                            ),
                            html.Div(
                                children=[
                                    html.Span(
                                        "OFF State (D conducting)",
                                        style={"fontWeight": "bold", "fontSize": "11px", "display": "block", "marginBottom": "4px"},
                                    ),
                                    html.Img(
                                        id="circuit-off-diagram",
                                        src="data:image/png;base64,",
                                        style={"height": "150px", "borderRadius": "4px"},
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            # Key equations section (expandable)
            html.Div(
                style={"padding": "12px", "borderBottom": "1px solid var(--grid-color)"},
                children=[
                    html.H3("Theoretical Formulas", style={"marginTop": "0"}),
                    dcc.Tabs(
                        id="equation-tabs",
                        children=[
                            dcc.Tab(
                                label="Voltage Conversion",
                                children=[
                                    html.Div(
                                        style={"padding": "8px", "fontSize": "12px", "fontFamily": "sans-serif"},
                                        children=[
                                            html.P(
                                                "Continuous Conduction Mode (CCM):",
                                                style={"fontWeight": "bold"},
                                            ),
                                            html.Div(
                                                id="eq-vout-ccm",
                                                style={
                                                    "padding": "8px",
                                                    "backgroundColor": "var(--bg-secondary)",
                                                    "borderRadius": "4px",
                                                    "marginBottom": "8px",
                                                    "fontFamily": "monospace",
                                                },
                                            ),
                                            html.P(
                                                "Discontinuous Conduction Mode (DCM):",
                                                style={"fontWeight": "bold", "marginTop": "12px"},
                                            ),
                                            html.Div(
                                                id="eq-vout-dcm",
                                                style={
                                                    "padding": "8px",
                                                    "backgroundColor": "var(--bg-secondary)",
                                                    "borderRadius": "4px",
                                                    "marginBottom": "8px",
                                                    "fontFamily": "monospace",
                                                },
                                            ),
                                            html.P(
                                                "Boundary Condition (k = 2Lf/R):",
                                                style={"fontWeight": "bold", "marginTop": "12px"},
                                            ),
                                            html.Div(
                                                id="eq-boundary",
                                                style={
                                                    "padding": "8px",
                                                    "backgroundColor": "var(--bg-secondary)",
                                                    "borderRadius": "4px",
                                                    "fontFamily": "monospace",
                                                },
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            dcc.Tab(
                                label="Ripple & Transient",
                                children=[
                                    html.Div(
                                        style={"padding": "8px", "fontSize": "12px", "fontFamily": "sans-serif"},
                                        children=[
                                            html.P(
                                                "Inductor Current Ripple (CCM):",
                                                style={"fontWeight": "bold"},
                                            ),
                                            html.Div(
                                                id="eq-ripple-il",
                                                style={
                                                    "padding": "8px",
                                                    "backgroundColor": "var(--bg-secondary)",
                                                    "borderRadius": "4px",
                                                    "marginBottom": "8px",
                                                    "fontFamily": "monospace",
                                                },
                                            ),
                                            html.P(
                                                "Output Voltage Ripple (with ESR):",
                                                style={"fontWeight": "bold", "marginTop": "12px"},
                                            ),
                                            html.Div(
                                                id="eq-ripple-vout",
                                                style={
                                                    "padding": "8px",
                                                    "backgroundColor": "var(--bg-secondary)",
                                                    "borderRadius": "4px",
                                                    "fontFamily": "monospace",
                                                },
                                            ),
                                            html.P(
                                                "Settling Time (transient):",
                                                style={"fontWeight": "bold", "marginTop": "12px"},
                                            ),
                                            html.Div(
                                                id="eq-settling",
                                                style={
                                                    "padding": "8px",
                                                    "backgroundColor": "var(--bg-secondary)",
                                                    "borderRadius": "4px",
                                                    "fontFamily": "monospace",
                                                },
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            dcc.Tab(
                                label="Efficiency & Losses",
                                children=[
                                    html.Div(
                                        style={"padding": "8px", "fontSize": "12px", "fontFamily": "sans-serif"},
                                        children=[
                                            html.P(
                                                "Converter Efficiency:",
                                                style={"fontWeight": "bold"},
                                            ),
                                            html.Div(
                                                id="eq-efficiency",
                                                style={
                                                    "padding": "8px",
                                                    "backgroundColor": "var(--bg-secondary)",
                                                    "borderRadius": "4px",
                                                    "marginBottom": "8px",
                                                    "fontFamily": "monospace",
                                                },
                                            ),
                                            html.P(
                                                "Components Stress (MOSFET):",
                                                style={"fontWeight": "bold", "marginTop": "12px"},
                                            ),
                                            html.Div(
                                                id="eq-stress",
                                                style={
                                                    "padding": "8px",
                                                    "backgroundColor": "var(--bg-secondary)",
                                                    "borderRadius": "4px",
                                                    "fontFamily": "monospace",
                                                },
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            # Operating region chart (DC-DC: CCM/DCM; Rectifier: alpha; Inverter: ma)
            html.Div(
                style={"padding": "12px", "borderBottom": "1px solid var(--grid-color)"},
                children=[
                    html.H3("Operating Region", style={"marginTop": "0"}),
                    dcc.Graph(
                        id="operating-region-graph",
                        config={"displaylogo": False, "responsive": True},
                        style={"height": "300px"},
                    ),
                    html.Span(
                        id="operating-region-note",
                        style={"fontSize": "10px", "color": "var(--text-secondary)", "marginTop": "8px", "display": "block"},
                        children="Current operating point shown as a red dot",
                    ),
                ],
            ),
            # Key waveform sketch (on-off-idle intervals annotated)
            html.Div(
                style={"padding": "12px"},
                children=[
                    html.H3("Ideal Waveform Sketch", style={"marginTop": "0"}),
                    html.Img(
                        id="waveform-sketch",
                        src="data:image/png;base64,",
                        style={"width": "100%", "maxWidth": "600px", "height": "auto"},
                    ),
                    html.Div(
                        style={
                            "marginTop": "8px",
                            "padding": "8px",
                            "backgroundColor": "var(--bg-secondary)",
                            "fontSize": "11px",
                            "borderRadius": "4px",
                        },
                        children=[
                            html.P(
                                "Blue regions: Switch ON (Q conducting)",
                                style={"color": "var(--accent-1)", "marginBottom": "4px"},
                            ),
                            html.P(
                                "Red regions: Switch OFF (D conducting)",
                                style={"color": "var(--accent-3)", "marginBottom": "4px"},
                            ),
                            html.P(
                                "Annotations: ΔIL = peak-to-peak current ripple, ΔVout = voltage ripple, DT = on-time, (1-D)T = off-time",
                                style={"color": "var(--text-secondary)", "fontSize": "10px"},
                            ),
                        ],
                    ),
                ],
            ),
        ],
        style={"backgroundColor": "var(--bg-primary)"},
    )
