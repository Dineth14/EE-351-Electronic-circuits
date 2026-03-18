"""Advanced sidebar with grouped parameters, presets, sweep mode, and simulation settings.

Features:
  - Parameter groups (Source, Converter, Load, Control, Non-idealities) with collapse/expand
  - Bidirectional slider/input synchronization
  - Parameter presets for realistic application scenarios
  - Parameter sweep mode (animates over swept parameter range)
  - Simulation settings (time to sim, points per cycle, solver selection)
  - Theme selector
  - Export buttons for all formats
"""

from __future__ import annotations

from dash import dcc, html, callback, Input, Output, State, clientside_callback
import json


# ==============================================================================
# PARAMETER PRESETS (Application scenarios)
# ==============================================================================

PARAMETER_PRESETS = {
    "custom": {
        "name": "Custom",
        "description": "User-defined parameters",
        "params": {},
    },
    "usb_5v_3v3": {
        "name": "5V → 3.3V USB",
        "description": "USB power bank auxiliary output",
        "params": {
            "V_in": 5.0,
            "V_out": 3.3,
            "P_out": 5.0,
            "f_sw": 500e3,
            "L": 2.2e-6,
            "C": 22e-6,
            "R_load": 2.18,
        },
    },
    "board_12v_5v": {
        "name": "12V → 5V Board",
        "description": "Main board supply regulation",
        "params": {
            "V_in": 12.0,
            "V_out": 5.0,
            "P_out": 15.0,
            "f_sw": 500e3,
            "L": 4.7e-6,
            "C": 47e-6,
            "R_load": 1.67,
        },
    },
    "ev_48v_12v": {
        "name": "48V → 12V EV Aux",
        "description": "Electric vehicle auxiliary power",
        "params": {
            "V_in": 48.0,
            "V_out": 12.0,
            "P_out": 120.0,
            "f_sw": 200e3,
            "L": 4.7e-6,
            "C": 44e-6,
            "R_load": 1.2,
        },
    },
    "pv_input_48v": {
        "name": "48V → 400V Solar",
        "description": "Solar PV boost converter to DC link",
        "params": {
            "V_in": 48.0,
            "V_out": 400.0,
            "P_out": 500.0,
            "f_sw": 100e3,
            "L": 10e-6,
            "C": 100e-6,
            "R_load": 320.0,
        },
    },
}


def sidebar_layout() -> html.Div:
    """Build complete advanced sidebar with all features.

    Returns
    -------
    html.Div
        Complete sidebar with parameter groups, presets, sweep, simulation
        settings, theme selector, and export buttons.
    """
    return html.Div(
        className="sidebar",
        children=[
            # ===== CONVERTER & CATEGORY SELECTION =====
            html.Div(
                style={
                    "padding": "12px",
                    "borderBottom": "1px solid var(--grid-color)",
                    "marginBottom": "8px",
                },
                children=[
                    html.Label("Converter Family:", style={"fontWeight": "bold", "fontSize": "12px"}),
                    dcc.Tabs(
                        id="category-tabs",
                        value="AC-DC",
                        children=[
                            dcc.Tab(label="AC-DC", value="AC-DC"),
                            dcc.Tab(label="DC-DC", value="DC-DC"),
                            dcc.Tab(label="DC-AC", value="DC-AC"),
                        ],
                        style={"marginBottom": "8px"},
                    ),
                    html.Label("Converter Model:", style={"fontWeight": "bold", "fontSize": "12px", "marginTop": "8px"}),
                    dcc.Dropdown(
                        id="converter-dropdown",
                        options=[],  # Populated via callback
                        value=None,
                        clearable=False,
                        style={"width": "100%"},
                    ),
                ],
            ),
            # ===== PARAMETER PRESETS =====
            html.Div(
                style={
                    "padding": "12px",
                    "borderBottom": "1px solid var(--grid-color)",
                    "marginBottom": "8px",
                },
                children=[
                    html.Label("Parameter Presets:", style={"fontWeight": "bold", "fontSize": "12px"}),
                    dcc.Dropdown(
                        id="preset-dropdown",
                        options=[{"label": v["name"], "value": k} for k, v in PARAMETER_PRESETS.items()],
                        value="custom",
                        clearable=False,
                        style={"width": "100%"},
                    ),
                    html.Div(
                        id="preset-description",
                        style={
                            "fontSize": "10px",
                            "color": "var(--text-secondary)",
                            "marginTop": "4px",
                            "fontStyle": "italic",
                        },
                    ),
                ],
            ),
            # ===== PARAMETER GROUPS (COLLAPSIBLE) =====
            html.Div(
                id="parameter-groups-container",
                style={
                    "marginBottom": "8px",
                    "maxHeight": "400px",
                    "overflowY": "auto",
                },
                children=[],  # Populated via callback
            ),
            # ===== PARAMETER SWEEP MODE =====
            html.Div(
                style={
                    "padding": "12px",
                    "backgroundColor": "var(--bg-secondary)",
                    "borderRadius": "4px",
                    "marginBottom": "8px",
                    "borderBottom": "1px solid var(--grid-color)",
                },
                children=[
                    html.Div(
                        style={"display": "flex", "alignItems": "center", "justifyContent": "space-between"},
                        children=[
                            html.Label(
                                "Parameter Sweep:",
                                style={"fontWeight": "bold", "fontSize": "12px", "margin": "0"},
                            ),
                            dcc.Checklist(
                                id="sweep-mode-toggle",
                                options=[{"label": " Enabled", "value": "enabled"}],
                                value=[],
                                style={"marginLeft": "auto"},
                            ),
                        ],
                    ),
                    html.Div(
                        id="sweep-controls",
                        style={"display": "none", "marginTop": "8px"},
                        children=[
                            html.Label("Sweep Parameter:", style={"fontSize": "11px", "marginTop": "4px"}),
                            dcc.Dropdown(
                                id="sweep-param-dropdown",
                                options=[],  # Populated via callback
                                value=None,
                                style={"width": "100%", "marginBottom": "8px"},
                            ),
                            html.Div(
                                style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "8px"},
                                children=[
                                    html.Div(
                                        children=[
                                            html.Label("From:", style={"fontSize": "10px"}),
                                            dcc.Input(
                                                id="sweep-start-input",
                                                type="number",
                                                value=0.1,
                                                style={"width": "100%", "padding": "4px"},
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        children=[
                                            html.Label("To:", style={"fontSize": "10px"}),
                                            dcc.Input(
                                                id="sweep-stop-input",
                                                type="number",
                                                value=0.8,
                                                style={"width": "100%", "padding": "4px"},
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            html.Label(
                                "Steps:",
                                style={"fontSize": "10px", "marginTop": "8px"},
                            ),
                            dcc.Input(
                                id="sweep-steps-input",
                                type="number",
                                value=10,
                                min=2,
                                max=50,
                                style={"width": "100%", "padding": "4px", "marginBottom": "8px"},
                            ),
                            html.Button(
                                "▶ Run Sweep",
                                id="run-sweep-btn",
                                n_clicks=0,
                                style={"width": "100%", "padding": "6px", "cursor": "pointer", "marginBottom": "4px"},
                            ),
                        ],
                    ),
                ],
            ),
            # ===== SIMULATION SETTINGS =====
            html.Div(
                style={
                    "padding": "12px",
                    "borderBottom": "1px solid var(--grid-color)",
                    "marginBottom": "8px",
                },
                children=[
                    html.Label(
                        "Simulation Settings",
                        style={"fontWeight": "bold", "fontSize": "12px", "marginBottom": "8px", "display": "block"},
                    ),
                    html.Label("Time to Simulate:", style={"fontSize": "11px"}),
                    dcc.Dropdown(
                        id="sim-time-dropdown",
                        options=[
                            {"label": "5 cycles", "value": "5_cycles"},
                            {"label": "10 cycles", "value": "10_cycles"},
                            {"label": "20 cycles", "value": "20_cycles"},
                            {"label": "50 cycles", "value": "50_cycles"},
                            {"label": "Custom (ms)", "value": "custom"},
                        ],
                        value="5_cycles",
                        style={"width": "100%", "marginBottom": "8px"},
                    ),
                    html.Label("Points per Cycle:", style={"fontSize": "11px"}),
                    dcc.RadioItems(
                        id="points-per-cycle-radio",
                        options=[
                            {"label": " 100", "value": "100"},
                            {"label": " 500", "value": "500"},
                            {"label": " 1000", "value": "1000"},
                            {"label": " 5000", "value": "5000"},
                        ],
                        value="500",
                        style={"fontSize": "10px"},
                    ),
                    html.Label(
                        "Solver:",
                        style={"fontSize": "11px", "marginTop": "8px"},
                    ),
                    dcc.RadioItems(
                        id="solver-radio",
                        options=[
                            {"label": " Fast (NumPy)", "value": "numpy"},
                            {"label": " Accurate (Radau ODE)", "value": "radau"},
                            {"label": " Ultra (RK45 + events)", "value": "rk45_events"},
                        ],
                        value="numpy",
                        style={"fontSize": "10px"},
                    ),
                    html.Span(
                        "ℹ Fast: ~100ms, Accurate: ~500ms, Ultra: ~2s",
                        style={
                            "fontSize": "9px",
                            "color": "var(--text-secondary)",
                            "display": "block",
                            "marginTop": "4px",
                        },
                    ),
                ],
            ),
            # ===== THEME SELECTOR =====
            html.Div(
                style={
                    "padding": "12px",
                    "borderBottom": "1px solid var(--grid-color)",
                    "marginBottom": "8px",
                },
                children=[
                    html.Label("Visual Theme:", style={"fontWeight": "bold", "fontSize": "12px"}),
                    dcc.RadioItems(
                        id="theme-selector",
                        options=[
                            {"label": " Oscilloscope", "value": "oscilloscope"},
                            {"label": " Dark Engineering", "value": "dark_engineering"},
                            {"label": " Light / Paper", "value": "light_paper"},
                        ],
                        value="oscilloscope",
                        style={"fontSize": "11px"},
                    ),
                ],
            ),
            # ===== SIMULATION CONTROL BUTTONS =====
            html.Div(
                style={"padding": "12px", "marginBottom": "8px"},
                children=[
                    html.Div(
                        style={"display": "grid", "gridTemplateColumns": "1fr 1fr 1fr", "gap": "4px", "marginBottom": "8px"},
                        children=[
                            html.Button(
                                "▶ Run",
                                id="run-btn",
                                n_clicks=0,
                                style={
                                    "padding": "8px",
                                    "fontWeight": "bold",
                                    "cursor": "pointer",
                                    "backgroundColor": "var(--accent-1)",
                                    "color": "#000",
                                    "border": "none",
                                    "borderRadius": "4px",
                                },
                            ),
                            html.Button(
                                "⏸ Pause",
                                id="pause-btn",
                                n_clicks=0,
                                style={
                                    "padding": "8px",
                                    "cursor": "pointer",
                                    "backgroundColor": "var(--accent-2)",
                                    "border": "none",
                                    "borderRadius": "4px",
                                },
                            ),
                            html.Button(
                                "↺ Reset",
                                id="reset-btn",
                                n_clicks=0,
                                style={
                                    "padding": "8px",
                                    "cursor": "pointer",
                                    "backgroundColor": "var(--bg-secondary)",
                                    "border": "1px solid var(--grid-color)",
                                    "borderRadius": "4px",
                                },
                            ),
                        ],
                    ),
                ],
            ),
            # ===== EXPORT BUTTONS =====
            html.Div(
                style={
                    "padding": "12px",
                    "borderTop": "1px solid var(--grid-color)",
                },
                children=[
                    html.Label("Export Results:", style={"fontWeight": "bold", "fontSize": "12px", "marginBottom": "8px", "display": "block"}),
                    html.Button(
                        "📥 PDF Report",
                        id="export-pdf-btn",
                        n_clicks=0,
                        style={"width": "100%", "padding": "6px", "marginBottom": "4px", "cursor": "pointer"},
                    ),
                    dcc.Download(id="download-pdf"),
                    html.Button(
                        "📊 CSV Data",
                        id="export-csv-btn",
                        n_clicks=0,
                        style={"width": "100%", "padding": "6px", "marginBottom": "4px", "cursor": "pointer"},
                    ),
                    dcc.Download(id="download-csv"),
                    html.Button(
                        "📈 PNG Image",
                        id="export-png-btn",
                        n_clicks=0,
                        style={"width": "100%", "padding": "6px", "marginBottom": "4px", "cursor": "pointer"},
                    ),
                    dcc.Download(id="download-png"),
                    html.Button(
                        "📋 JSON",
                        id="export-json-btn",
                        n_clicks=0,
                        style={"width": "100%", "padding": "6px", "cursor": "pointer"},
                    ),
                    dcc.Download(id="download-json"),
                ],
            ),
            # Hidden store for sweep results
            dcc.Store(id="sweep-results-store"),
        ],
        style={
            "width": "280px",
            "backgroundColor": "var(--bg-primary)",
            "borderRight": "1px solid var(--grid-color)",
            "overflowY": "auto",
            "height": "100vh",
        },
    )


def create_collapsible_group(group_name: str, group_label: str, params: dict[str, dict]) -> html.Details:
    """Create a collapsible parameter group.

    Parameters
    ----------
    group_name:
        Internal identifier (e.g., 'source_params').
    group_label:
        Display label (e.g., 'Source Parameters').
    params:
        Parameter schema dictionary.

    Returns
    -------
    html.Details
        Collapsible group with parameters.
    """
    controls = []
    for param_name, param_spec in params.items():
        controls.append(_create_param_control(param_name, param_spec))

    return html.Details(
        open=True,
        children=[
            html.Summary(
                group_label,
                style={
                    "fontWeight": "bold",
                    "cursor": "pointer",
                    "padding": "6px",
                    "userSelect": "none",
                },
            ),
            html.Div(
                style={"paddingLeft": "12px", "borderLeft": "2px solid var(--accent-1)"},
                children=controls,
            ),
        ],
        style={"marginBottom": "8px"},
    )


def _create_param_control(param_name: str, spec: dict[str, float | str]) -> html.Div:
    """Create a single parameter slider + input control.

    Parameters
    ----------
    param_name:
        Parameter name (e.g., 'L', 'C').
    spec:
        Parameter specification dictionary.

    Returns
    -------
    html.Div
        Control row with label, slider, and numeric input.
    """
    min_v = float(spec.get("min", 0.0))
    max_v = float(spec.get("max", 1.0))
    step = float(spec.get("step", 0.01))
    default = float(spec.get("default", min_v))
    label = str(spec.get("label", param_name))
    unit = str(spec.get("unit", ""))

    return html.Div(
        style={"marginBottom": "10px", "padding": "4px"},
        children=[
            html.Div(
                style={"display": "flex", "justifyContent": "space-between", "marginBottom": "4px"},
                children=[
                    html.Label(label, style={"fontSize": "10px", "fontWeight": "bold"}),
                    html.Span(unit, style={"fontSize": "9px", "color": "var(--text-secondary)"}),
                ],
            ),
            dcc.Slider(
                id={"type": "param-slider", "index": param_name},
                min=min_v,
                max=max_v,
                step=step,
                value=default,
                tooltip={"placement": "bottom", "always_visible": False},
                marks={min_v: f"{min_v:.2g}", max_v: f"{max_v:.2g}"},
            ),
            dcc.Input(
                id={"type": "param-input", "index": param_name},
                type="number",
                min=min_v,
                max=max_v,
                step=step,
                value=default,
                style={"width": "100%", "padding": "4px", "marginTop": "4px", "fontSize": "10px"},
            ),
        ],
    )
