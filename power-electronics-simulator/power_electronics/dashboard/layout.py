"""Dash layout definition for the simulator application."""

from __future__ import annotations

from dash import dcc, html

from power_electronics.converters import CONVERTER_REGISTRY
from power_electronics.dashboard.components.metrics_panel import metrics_panel
from power_electronics.dashboard.components.sidebar import build_param_controls, sidebar_layout
from power_electronics.dashboard.components.spectrum_panel import spectrum_panel
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
            html.Div(
                className="top-bar",
                children=[
                    html.H1("⚡ Power Electronics Simulator"),
                    html.A("GitHub", href="https://github.com/example/power-electronics-simulator", target="_blank"),
                    dcc.Dropdown(
                        id="theme-toggle",
                        options=[
                            {"label": "Oscilloscope", "value": "oscilloscope"},
                            {"label": "Dark", "value": "dark"},
                            {"label": "Light", "value": "light"},
                        ],
                        value="oscilloscope",
                        clearable=False,
                        style={"width": "180px"},
                    ),
                ],
            ),
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
                                    dcc.Tab(label="Waveforms", value="waveforms", children=[waveform_panel()]),
                                    dcc.Tab(label="Metrics Dashboard", value="metrics", children=[metrics_panel()]),
                                    dcc.Tab(label="Frequency Spectrum", value="spectrum", children=[spectrum_panel()]),
                                    dcc.Tab(
                                        label="Theory & Equations",
                                        value="theory",
                                        children=[html.Div(id="theory-panel", className="panel theory-panel")],
                                    ),
                                ],
                            )
                        ],
                    ),
                ],
            ),
            dcc.Store(id="result-store"),
            dcc.Store(id="history-store", data=[]),
            dcc.Interval(id="sweep-interval", interval=400, n_intervals=0, disabled=True),
            dcc.Loading(id="global-loading", type="dot", children=html.Div(id="loading-anchor")),
        ],
    )
