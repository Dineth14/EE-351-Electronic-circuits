"""Instrument-grade metrics dashboard panel with KPI cards, power flow diagram,
theory-vs-simulation comparison, and historical comparison table.
"""

from dash import dash_table, dcc, html


def metrics_panel() -> html.Div:
    """Build metrics dashboard with cards, power flow, and comparison table."""
    return html.Div(
        className="panel metrics-panel",
        children=[
            # ── Top: KPI metric cards ──────────────────────────────────
            html.Div(
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "flex-start",
                    "gap": "12px",
                    "flexWrap": "wrap",
                    "padding": "8px 0",
                },
                children=[
                    html.Div(
                        id="metric-cards",
                        className="metric-grid",
                        style={"flex": "1", "minWidth": "300px"},
                    ),
                    html.Div(
                        id="power-flow-display",
                        style={
                            "minWidth": "220px",
                            "padding": "10px",
                            "borderRadius": "8px",
                            "border": "1px solid var(--grid-color, #26344c)",
                            "background": "var(--bg-alt, #141925)",
                            "fontSize": "11px",
                            "fontFamily": "'JetBrains Mono', monospace",
                        },
                    ),
                ],
            ),
            # ── Middle: Theory vs Simulation ───────────────────────────
            html.Div(
                style={
                    "marginTop": "10px",
                    "padding": "8px",
                    "borderRadius": "6px",
                    "border": "1px solid var(--grid-color, #26344c)",
                    "background": "var(--bg-alt, #141925)",
                },
                children=[
                    html.H4(
                        "Theory vs Simulation",
                        style={"fontSize": "12px", "margin": "0 0 6px 0"},
                    ),
                    html.Div(id="theory-vs-sim-table"),
                ],
            ),
            # ── Bottom: Comparison history table ───────────────────────
            html.Div(
                style={"marginTop": "10px"},
                children=[
                    html.H4(
                        "Run Comparison History",
                        style={"fontSize": "12px", "margin": "0 0 6px 0"},
                    ),
                    dash_table.DataTable(
                        id="comparison-table",
                        page_size=8,
                        sort_action="native",
                        filter_action="native",
                        style_table={"overflowX": "auto"},
                        style_header={
                            "backgroundColor": "var(--bg-alt, #141925)",
                            "color": "var(--text, #dfffe9)",
                            "fontWeight": "bold",
                            "fontSize": "11px",
                            "borderBottom": "2px solid var(--accent, #00ff88)",
                        },
                        style_cell={
                            "backgroundColor": "var(--bg-panel, #11131a)",
                            "color": "var(--text, #dfffe9)",
                            "fontSize": "10px",
                            "fontFamily": "'JetBrains Mono', monospace",
                            "padding": "4px 8px",
                            "border": "1px solid var(--grid-color, #26344c)",
                        },
                        style_data_conditional=[
                            {
                                "if": {"row_index": "odd"},
                                "backgroundColor": "var(--bg-alt, #141925)",
                            }
                        ],
                    ),
                ],
            ),
            # ── Efficiency gauge placeholder ──────────────────────────
            dcc.Graph(
                id="efficiency-gauge",
                config={"displaylogo": False, "staticPlot": True},
                style={"height": "180px", "marginTop": "10px"},
            ),
        ],
    )
