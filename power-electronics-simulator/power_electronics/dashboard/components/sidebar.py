"""Production-grade sidebar with grouped parameters, presets, sweep mode,
simulation settings, and export controls.
"""

from __future__ import annotations

from dash import dcc, html


# ---------------------------------------------------------------------------
# Parameter presets — realistic application scenarios
# ---------------------------------------------------------------------------

PARAMETER_PRESETS: dict[str, dict] = {
    "custom": {
        "name": "Custom",
        "description": "User-defined parameters",
        "params": {},
    },
    "usb_5v_3v3": {
        "name": "5 V → 3.3 V USB",
        "description": "USB power-bank auxiliary output — low-power buck",
        "params": {
            "V_in": 5.0, "V_out": 3.3, "P_out": 5.0,
            "f_sw": 500e3, "L": 2.2e-6, "C": 22e-6, "R_load": 2.18,
        },
    },
    "board_12v_5v": {
        "name": "12 V → 5 V Board",
        "description": "Main board supply regulation — medium buck",
        "params": {
            "V_in": 12.0, "V_out": 5.0, "P_out": 15.0,
            "f_sw": 500e3, "L": 4.7e-6, "C": 47e-6, "R_load": 1.67,
        },
    },
    "ev_48v_12v": {
        "name": "48 V → 12 V EV Aux",
        "description": "Electric vehicle auxiliary power — high-current buck",
        "params": {
            "V_in": 48.0, "V_out": 12.0, "P_out": 120.0,
            "f_sw": 200e3, "L": 4.7e-6, "C": 44e-6, "R_load": 1.2,
        },
    },
    "pv_input_48v": {
        "name": "48 V → 400 V Solar",
        "description": "Solar PV boost converter to DC link — high voltage",
        "params": {
            "V_in": 48.0, "V_out": 400.0, "P_out": 500.0,
            "f_sw": 100e3, "L": 10e-6, "C": 100e-6, "R_load": 320.0,
        },
    },
}


# ---------------------------------------------------------------------------
# Dynamic parameter controls (used by callbacks.py)
# ---------------------------------------------------------------------------

def build_param_controls(schema: dict[str, dict[str, float | str]]) -> list:
    """Build Dash control components from a converter parameter schema.

    Parameters
    ----------
    schema
        ``{param_name: {type, min, max, step, default, unit, label}}``.

    Returns
    -------
    list[html.Div]
        One slider + numeric-input row per parameter, grouped by category.
    """
    groups: dict[str, list] = {}
    for param_name, spec in schema.items():
        group = _classify_param(param_name)
        groups.setdefault(group, []).append(
            _create_param_control(param_name, spec)
        )

    controls: list = []
    for group_name, items in groups.items():
        controls.append(
            html.Div(
                className="param-group",
                children=[
                    html.Div(
                        className="param-head",
                        children=[
                            html.Span(
                                group_name,
                                style={
                                    "fontWeight": "bold",
                                    "fontSize": "10px",
                                    "color": "var(--accent, #00ff88)",
                                    "textTransform": "uppercase",
                                    "letterSpacing": "0.5px",
                                },
                            ),
                        ],
                    ),
                    *items,
                ],
            )
        )
    return controls


def _classify_param(name: str) -> str:
    """Assign a parameter to a logical group for sidebar rendering."""
    n = name.lower()
    if any(k in n for k in ("vin", "vac", "vdc", "v_in", "v_out")):
        return "Voltage"
    if any(k in n for k in ("freq", "f_", "f_sw", "f_carrier", "f_output")):
        return "Frequency"
    if any(k in n for k in ("duty", "modulation", "alpha", "control")):
        return "Control"
    if any(k in n for k in ("l_", "c_", "l ", "c ", "inductance", "capacitance")):
        return "Passives"
    if any(k in n for k in ("r_load", "r_l", "load", "esr")):
        return "Load & Parasitics"
    if any(k in n for k in ("n", "turns")):
        return "Transformer"
    return "Parameters"


# ---------------------------------------------------------------------------
# Full sidebar layout (used by layout.py)
# ---------------------------------------------------------------------------

def sidebar_layout(
    categories: list[str],
    converters: list[dict],
    controls: list,
) -> html.Div:
    """Build the complete sidebar.

    Parameters
    ----------
    categories
        Converter family names, e.g. ``["AC-DC", "DC-DC", "DC-AC"]``.
    converters
        Options list for the converter dropdown.
    controls
        Pre-built parameter control components (from ``build_param_controls``).
    """
    return html.Div(
        className="sidebar",
        children=[
            # ── Converter & Category Selection ─────────────────────────
            html.Div(
                style={"padding": "12px", "borderBottom": "1px solid var(--grid-color, #333)"},
                children=[
                    html.Label(
                        "Converter Family:",
                        style={
                            "fontWeight": "bold",
                            "fontSize": "11px",
                            "display": "block",
                            "color": "var(--accent, #00ff88)",
                            "textTransform": "uppercase",
                            "letterSpacing": "0.5px",
                            "marginBottom": "4px",
                        },
                    ),
                    dcc.Tabs(
                        id="category-tabs",
                        value=categories[0] if categories else "AC-DC",
                        children=[dcc.Tab(label=c, value=c) for c in categories],
                        style={"marginBottom": "8px"},
                    ),
                    html.Label(
                        "Converter Model:",
                        style={
                            "fontWeight": "bold",
                            "fontSize": "11px",
                            "marginTop": "8px",
                            "display": "block",
                        },
                    ),
                    dcc.Dropdown(
                        id="converter-dropdown",
                        options=converters,
                        value=converters[0]["value"] if converters else None,
                        clearable=False,
                        style={"width": "100%"},
                    ),
                ],
            ),
            # ── Parameter Presets ──────────────────────────────────────
            html.Div(
                style={"padding": "12px", "borderBottom": "1px solid var(--grid-color, #333)"},
                children=[
                    html.Label(
                        "Parameter Presets:",
                        style={
                            "fontWeight": "bold",
                            "fontSize": "11px",
                            "display": "block",
                        },
                    ),
                    dcc.Dropdown(
                        id="preset-dropdown",
                        options=[
                            {"label": v["name"], "value": k}
                            for k, v in PARAMETER_PRESETS.items()
                        ],
                        value="custom",
                        clearable=False,
                        style={"width": "100%"},
                    ),
                    html.Div(
                        id="preset-description",
                        style={
                            "fontSize": "10px",
                            "color": "var(--muted, #7a8ca5)",
                            "marginTop": "4px",
                            "fontStyle": "italic",
                        },
                    ),
                ],
            ),
            # ── Parameter Controls (replaced dynamically) ─────────────
            html.Div(
                id="param-controls",
                children=controls,
                style={
                    "maxHeight": "320px",
                    "overflowY": "auto",
                    "padding": "8px",
                    "borderBottom": "1px solid var(--grid-color, #333)",
                },
            ),
            # ── Simulation Settings ────────────────────────────────────
            html.Div(
                style={"padding": "12px", "borderBottom": "1px solid var(--grid-color, #333)"},
                children=[
                    html.Label(
                        "Simulation Settings",
                        style={
                            "fontWeight": "bold",
                            "fontSize": "11px",
                            "marginBottom": "8px",
                            "display": "block",
                            "color": "var(--accent, #00ff88)",
                            "textTransform": "uppercase",
                            "letterSpacing": "0.5px",
                        },
                    ),
                    html.Label("Time to Simulate:", style={"fontSize": "10px"}),
                    dcc.Dropdown(
                        id="sim-time-dropdown",
                        options=[
                            {"label": "5 cycles", "value": "5"},
                            {"label": "10 cycles", "value": "10"},
                            {"label": "20 cycles", "value": "20"},
                            {"label": "50 cycles", "value": "50"},
                        ],
                        value="10",
                        clearable=False,
                        style={"width": "100%", "marginBottom": "8px"},
                    ),
                    html.Label("Points per Cycle:", style={"fontSize": "10px"}),
                    dcc.RadioItems(
                        id="points-per-cycle-radio",
                        options=[
                            {"label": " 100", "value": "100"},
                            {"label": " 500", "value": "500"},
                            {"label": " 1000", "value": "1000"},
                        ],
                        value="500",
                        style={"fontSize": "10px"},
                        inline=True,
                    ),
                    html.Label(
                        "Solver:",
                        style={"fontSize": "10px", "marginTop": "8px"},
                    ),
                    dcc.RadioItems(
                        id="solver-radio",
                        options=[
                            {"label": " Fast (NumPy)", "value": "numpy"},
                            {"label": " Accurate (Radau)", "value": "radau"},
                            {"label": " Ultra (RK45 + events)", "value": "rk45_events"},
                        ],
                        value="numpy",
                        style={"fontSize": "10px"},
                    ),
                ],
            ),
            # ── Export Controls ────────────────────────────────────────
            html.Div(
                style={"padding": "12px", "borderBottom": "1px solid var(--grid-color, #333)"},
                children=[
                    html.Label(
                        "Export",
                        style={
                            "fontWeight": "bold",
                            "fontSize": "11px",
                            "display": "block",
                            "marginBottom": "6px",
                            "color": "var(--accent, #00ff88)",
                            "textTransform": "uppercase",
                            "letterSpacing": "0.5px",
                        },
                    ),
                    html.Div(
                        style={"display": "flex", "gap": "6px", "flexWrap": "wrap"},
                        children=[
                            html.Button(
                                "CSV",
                                id="export-csv-btn",
                                n_clicks=0,
                                style={
                                    "flex": "1",
                                    "padding": "6px",
                                    "fontSize": "10px",
                                    "cursor": "pointer",
                                    "minWidth": "50px",
                                },
                            ),
                            html.Button(
                                "JSON",
                                id="export-json-btn",
                                n_clicks=0,
                                style={
                                    "flex": "1",
                                    "padding": "6px",
                                    "fontSize": "10px",
                                    "cursor": "pointer",
                                    "minWidth": "50px",
                                },
                            ),
                            html.Button(
                                "PNG",
                                id="export-png-btn",
                                n_clicks=0,
                                style={
                                    "flex": "1",
                                    "padding": "6px",
                                    "fontSize": "10px",
                                    "cursor": "pointer",
                                    "minWidth": "50px",
                                },
                            ),
                            html.Button(
                                "PDF",
                                id="export-pdf-btn",
                                n_clicks=0,
                                style={
                                    "flex": "1",
                                    "padding": "6px",
                                    "fontSize": "10px",
                                    "cursor": "pointer",
                                    "minWidth": "50px",
                                },
                            ),
                        ],
                    ),
                    dcc.Download(id="export-download"),
                ],
            ),
            # ── Run / Reset buttons ───────────────────────────────────
            html.Div(
                style={"padding": "12px"},
                children=[
                    html.Button(
                        "\u25b6  Run Simulation",
                        id="run-btn",
                        n_clicks=0,
                        style={
                            "width": "100%",
                            "padding": "10px",
                            "fontWeight": "bold",
                            "cursor": "pointer",
                            "backgroundColor": "var(--accent, #00ff88)",
                            "color": "#000",
                            "border": "none",
                            "borderRadius": "4px",
                            "marginBottom": "6px",
                            "fontSize": "12px",
                            "letterSpacing": "0.3px",
                        },
                    ),
                    html.Button(
                        "\u21ba  Reset",
                        id="reset-btn",
                        n_clicks=0,
                        style={
                            "width": "100%",
                            "padding": "8px",
                            "cursor": "pointer",
                            "border": "1px solid var(--grid-color, #333)",
                            "borderRadius": "4px",
                            "backgroundColor": "transparent",
                            "color": "var(--text, #dfffe9)",
                            "fontSize": "11px",
                        },
                    ),
                ],
            ),
        ],
        style={
            "width": "280px",
            "backgroundColor": "var(--bg-panel, #11131a)",
            "borderRight": "1px solid var(--grid-color, #26344c)",
            "overflowY": "auto",
            "height": "100vh",
        },
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_param_control(param_name: str, spec: dict) -> html.Div:
    """Build one slider + numeric-input row for a single parameter."""
    min_v = float(spec.get("min", 0.0))
    max_v = float(spec.get("max", 1.0))
    step = float(spec.get("step", 0.01))
    default = float(spec.get("default", min_v))
    label = str(spec.get("label", param_name))
    unit = str(spec.get("unit", ""))

    return html.Div(
        style={"marginBottom": "8px", "padding": "4px"},
        children=[
            html.Div(
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "marginBottom": "2px",
                },
                children=[
                    html.Label(
                        label,
                        style={
                            "fontSize": "10px",
                            "fontWeight": "bold",
                        },
                    ),
                    html.Span(
                        unit,
                        style={
                            "fontSize": "9px",
                            "color": "var(--muted, #7a8ca5)",
                        },
                    ),
                ],
            ),
            dcc.Slider(
                id={"type": "param-slider", "name": param_name},
                min=min_v,
                max=max_v,
                step=step,
                value=default,
                tooltip={"placement": "bottom", "always_visible": False},
                marks={min_v: f"{min_v:.2g}", max_v: f"{max_v:.2g}"},
            ),
            dcc.Input(
                id={"type": "param-input", "name": param_name},
                type="number",
                min=min_v,
                max=max_v,
                step=step,
                value=default,
                style={
                    "width": "100%",
                    "padding": "4px",
                    "marginTop": "2px",
                    "fontSize": "10px",
                    "background": "var(--bg-alt, #141925)",
                    "border": "1px solid var(--grid-color, #26344c)",
                    "color": "var(--text, #dfffe9)",
                    "borderRadius": "3px",
                },
            ),
        ],
    )
