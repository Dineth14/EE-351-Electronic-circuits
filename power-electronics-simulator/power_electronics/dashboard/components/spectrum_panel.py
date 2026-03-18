"""Dual-panel harmonic spectrum and analysis.

Features:
  - Amplitude spectrum (V or dBV selectable)
  - Phase spectrum
  - Harmonic table with amplitudes and % of fundamental
  - THD gauge with color zones (excellent/good/fair/poor)
  - Optional output filter simulation
  - Spectrogram view (time-frequency evolution)
"""

from dash import dcc, html, dash_table


def spectrum_panel() -> html.Div:
    """Build dual-panel harmonic spectrum panel.

    Returns
    -------
    html.Div
        Complete spectrum analysis panel with amplitude/phase plots,
        harmonic table, THD gauge, and optional filter simulation.
    """
    return html.Div(
        className="spectrum-panel",
        children=[
            # Top controls
            html.Div(
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "12px",
                    "padding": "8px",
                    "borderBottom": "1px solid var(--grid-color)",
                    "marginBottom": "8px",
                },
                children=[
                    html.Label("Amplitude Scale:", style={"fontWeight": "bold"}),
                    dcc.RadioItems(
                        id="spectrum-scale-radio",
                        options=[
                            {"label": " Linear (V)", "value": "linear"},
                            {"label": " dBV", "value": "dbv"},
                            {"label": " % of Fund.", "value": "percent"},
                        ],
                        value="linear",
                        inline=True,
                        style={"display": "flex", "gap": "16px"},
                    ),
                    html.Button(
                        "Toggle Filter Sim",
                        id="filter-sim-toggle-btn",
                        n_clicks=0,
                        style={
                            "marginLeft": "auto",
                            "padding": "6px 12px",
                            "cursor": "pointer",
                        },
                    ),
                    html.Button(
                        "Spectrogram View",
                        id="spectrogram-view-btn",
                        n_clicks=0,
                        style={"padding": "6px 12px", "cursor": "pointer"},
                    ),
                ],
            ),
            # Dual panel: amplitude + phase spectrum
            html.Div(
                style={
                    "display": "grid",
                    "gridTemplateColumns": "1fr 1fr",
                    "gap": "8px",
                    "marginBottom": "12px",
                },
                children=[
                    html.Div(
                        children=[
                            html.Span(
                                "Amplitude Spectrum",
                                style={"fontWeight": "bold", "fontSize": "12px", "display": "block", "marginBottom": "4px"},
                            ),
                            dcc.Graph(
                                id="spectrum-amplitude-graph",
                                config={"displaylogo": False, "responsive": True},
                                style={"height": "300px"},
                            ),
                        ],
                    ),
                    html.Div(
                        children=[
                            html.Span(
                                "Phase Spectrum",
                                style={"fontWeight": "bold", "fontSize": "12px", "display": "block", "marginBottom": "4px"},
                            ),
                            dcc.Graph(
                                id="spectrum-phase-graph",
                                config={"displaylogo": False, "responsive": True},
                                style={"height": "300px"},
                            ),
                        ],
                    ),
                ],
            ),
            # THD Gauge (circular)
            html.Div(
                style={
                    "display": "flex",
                    "justifyContent": "center",
                    "alignItems": "center",
                    "marginBottom": "12px",
                    "padding": "8px",
                    "borderBottom": "1px solid var(--grid-color)",
                },
                children=[
                    html.Div(
                        children=[
                            dcc.Graph(
                                id="thd-gauge-graph",
                                config={"displaylogo": False},
                                style={"height": "200px", "width": "250px"},
                            ),
                        ],
                    ),
                ],
            ),
            # Harmonic Table
            html.Div(
                style={"marginBottom": "12px", "padding": "8px", "borderBottom": "1px solid var(--grid-color)"},
                children=[
                    html.Span(
                        "Harmonic Spectrum Table",
                        style={"fontWeight": "bold", "display": "block", "marginBottom": "8px"},
                    ),
                    dash_table.DataTable(
                        id="harmonic-table",
                        columns=[
                            {"name": "Order", "id": "order"},
                            {"name": "Freq (Hz)", "id": "freq"},
                            {"name": "Amplitude (V)", "id": "amplitude_v"},
                            {"name": "Amplitude (dBV)", "id": "amplitude_dbv"},
                            {"name": "Phase (°)", "id": "phase_deg"},
                            {"name": "% of Fund.", "id": "percent_fund"},
                        ],
                        data=[
                            {
                                "order": "1",
                                "freq": "50.0",
                                "amplitude_v": "12.43",
                                "amplitude_dbv": "21.89",
                                "phase_deg": "0.0",
                                "percent_fund": "100.0",
                            },
                            {
                                "order": "3",
                                "freq": "150.0",
                                "amplitude_v": "0.42",
                                "amplitude_dbv": "2.46",
                                "phase_deg": "12.4",
                                "percent_fund": "3.38",
                            },
                            {
                                "order": "5",
                                "freq": "250.0",
                                "amplitude_v": "0.18",
                                "amplitude_dbv": "-4.89",
                                "phase_deg": "28.1",
                                "percent_fund": "1.45",
                            },
                            {
                                "order": "7",
                                "freq": "350.0",
                                "amplitude_v": "0.09",
                                "amplitude_dbv": "-16.18",
                                "phase_deg": "45.3",
                                "percent_fund": "0.72",
                            },
                        ],
                        style_cell={
                            "padding": "4px",
                            "fontSize": "11px",
                            "textAlign": "center",
                        },
                        style_header={
                            "backgroundColor": "var(--accent-2)",
                            "fontWeight": "bold",
                            "color": "var(--bg-primary)",
                        },
                        page_size=8,
                    ),
                ],
            ),
            # Filter Simulation Panel (hidden by default, toggleable)
            html.Div(
                id="filter-sim-panel",
                style={"display": "none", "padding": "12px", "borderTop": "1px solid var(--grid-color)"},
                children=[
                    html.Div(
                        style={"display": "grid", "gridTemplateColumns": "1fr 1fr 1fr", "gap": "12px", "marginBottom": "8px"},
                        children=[
                            html.Div(
                                children=[
                                    html.Label("Filter L (mH):", style={"fontSize": "11px"}),
                                    dcc.Slider(
                                        id="filter-l-slider",
                                        min=0.1,
                                        max=10,
                                        step=0.1,
                                        value=1.0,
                                        marks={0.1: "0.1", 5: "5", 10: "10"},
                                    ),
                                ],
                            ),
                            html.Div(
                                children=[
                                    html.Label("Filter C (µF):", style={"fontSize": "11px"}),
                                    dcc.Slider(
                                        id="filter-c-slider",
                                        min=1,
                                        max=100,
                                        step=1,
                                        value=10,
                                        marks={1: "1", 50: "50", 100: "100"},
                                    ),
                                ],
                            ),
                            html.Div(
                                children=[
                                    html.Label("Cutoff Freq (kHz):", style={"fontSize": "11px"}),
                                    html.Div(
                                        id="filter-cutoff-display",
                                        style={
                                            "fontSize": "14px",
                                            "fontWeight": "bold",
                                            "color": "var(--accent-1)",
                                        },
                                    ),
                                ],
                            ),
                        ],
                    ),
                    html.Span(
                        "Spectrum after filter:",
                        style={"fontWeight": "bold", "display": "block", "marginBottom": "8px"},
                    ),
                    dcc.Graph(
                        id="filtered-spectrum-graph",
                        config={"displaylogo": False, "responsive": True},
                        style={"height": "250px"},
                    ),
                    html.Div(
                        id="filter-effect-text",
                        style={"fontSize": "11px", "marginTop": "8px", "color": "var(--text-secondary)"},
                    ),
                ],
            ),
        ],
        style={"padding": "8px", "backgroundColor": "var(--bg-primary)"},
    )
