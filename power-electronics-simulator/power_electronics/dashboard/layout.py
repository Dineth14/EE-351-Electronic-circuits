"""Dash layout definition for the simulator application.

Defines the complete app structure: top bar with branding and theme selector,
sidebar with converter selection and parameters, and tabbed main content
with waveform, metrics, spectrum, and theory panels.
"""

from __future__ import annotations

from dash import dcc, html

from power_electronics.converters import CONVERTER_REGISTRY
from power_electronics.dashboard.components.metrics_panel import metrics_panel
from power_electronics.dashboard.components.sidebar import build_param_controls, sidebar_layout
from power_electronics.dashboard.components.spectrum_panel import spectrum_panel
from power_electronics.dashboard.components.theory_panel import theory_panel
from power_electronics.dashboard.components.waveform_panel import waveform_panel


def build_layout() -> html.Div:
    """Create app layout with top bar, sidebar, and tabbed content."""
    default_key = list(CONVERTER_REGISTRY.keys())[0]
    default_schema = CONVERTER_REGISTRY[default_key].get_param_schema()
    categories = ["AC-DC", "DC-AC", "DC-DC"]
    converters = [{"label": key, "value": key} for key in CONVERTER_REGISTRY]
    controls = build_param_controls(default_schema)

    return html.Div(
        className="app-shell",
        children=[
            # ── Top Bar ────────────────────────────────────────────────
            html.Div(
                className="top-bar",
                children=[
                    html.Div(
                        style={"display": "flex", "alignItems": "center", "gap": "10px"},
                        children=[
                            html.Span("⚡", style={"fontSize": "1.6rem"}),
                            html.H1(
                                "Power Electronics Simulator",
                                style={"margin": "0", "fontSize": "1.3rem"},
                            ),
                            html.Span(
                                "v1.0",
                                style={
                                    "fontSize": "0.7rem",
                                    "color": "var(--muted, #7a8ca5)",
                                    "alignSelf": "flex-end",
                                    "marginBottom": "2px",
                                },
                            ),
                        ],
                    ),
                    html.Div(
                        style={"display": "flex", "alignItems": "center", "gap": "12px"},
                        children=[
                            html.Div(
                                id="sim-status",
                                style={
                                    "fontSize": "10px",
                                    "fontFamily": "'JetBrains Mono', monospace",
                                    "color": "var(--muted, #7a8ca5)",
                                },
                            ),
                            dcc.Dropdown(
                                id="theme-toggle",
                                options=[
                                    {"label": "🟢 Oscilloscope", "value": "oscilloscope"},
                                    {"label": "🔵 Dark Engineering", "value": "dark"},
                                    {"label": "⚪ Light Paper", "value": "light"},
                                ],
                                value="oscilloscope",
                                clearable=False,
                                style={"width": "200px"},
                            ),
                        ],
                    ),
                ],
            ),
            # ── Body: Sidebar + Main Content ───────────────────────────
            html.Div(
                className="body-grid",
                children=[
                    sidebar_layout(categories, converters, controls),
                    html.Div(
                        className="main-content",
                        children=[
                            dcc.Tabs(
                                id="main-tabs",
                                value="waveforms",
                                children=[
                                    dcc.Tab(
                                        label="📈 Waveforms",
                                        value="waveforms",
                                        children=[waveform_panel()],
                                    ),
                                    dcc.Tab(
                                        label="📊 Metrics",
                                        value="metrics",
                                        children=[metrics_panel()],
                                    ),
                                    dcc.Tab(
                                        label="📐 Spectrum",
                                        value="spectrum",
                                        children=[spectrum_panel()],
                                    ),
                                    dcc.Tab(
                                        label="📖 Theory",
                                        value="theory",
                                        children=[theory_panel()],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            # ── Hidden Stores & Intervals ──────────────────────────────
            dcc.Store(id="result-store"),
            dcc.Store(id="history-store", data=[]),
            dcc.Interval(id="sweep-interval", interval=400, n_intervals=0, disabled=True),
            dcc.Loading(id="global-loading", type="dot", children=html.Div(id="loading-anchor")),
        ],
    )
