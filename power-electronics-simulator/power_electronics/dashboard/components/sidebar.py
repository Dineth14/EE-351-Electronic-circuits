"""Sidebar with converter selection and dynamic parameter controls."""

from __future__ import annotations

from dash import dcc, html


def _param_control(name: str, schema: dict[str, float | str]):
    min_v = float(schema.get("min", 0.0))
    max_v = float(schema.get("max", 1.0))
    step = float(schema.get("step", 0.01))
    default = float(schema.get("default", min_v)) if schema.get("type") != "string" else schema.get("default", "")
    label = str(schema.get("label", name))
    unit = str(schema.get("unit", ""))
    if schema.get("type") == "string":
        return html.Div(
            className="param-group",
            children=[
                html.Label(f"{label}"),
                dcc.Input(id={"type": "param-input", "name": name}, type="text", value=str(default), debounce=True),
            ],
        )
    return html.Div(
        className="param-group",
        children=[
            html.Div(className="param-head", children=[html.Label(label), html.Span(unit, className="param-unit")]),
            dcc.Slider(
                id={"type": "param-slider", "name": name},
                min=min_v,
                max=max_v,
                step=step,
                value=float(default),
                tooltip={"placement": "bottom", "always_visible": False},
            ),
            dcc.Input(
                id={"type": "param-input", "name": name},
                type="number",
                min=min_v,
                max=max_v,
                step=step,
                value=float(default),
                debounce=True,
            ),
        ],
    )


def build_param_controls(schema: dict[str, dict[str, float | str]]) -> list:
    """Generate slider/input pairs from converter parameter schema."""
    return [_param_control(name, spec) for name, spec in schema.items()]


def sidebar_layout(categories: list[str], converters: list[dict[str, str]], controls: list) -> html.Div:
    """Build full sidebar with category tabs and run controls."""
    return html.Div(
        className="sidebar",
        children=[
            dcc.Tabs(
                id="category-tabs",
                value=categories[0] if categories else "AC-DC",
                children=[dcc.Tab(label=c, value=c) for c in categories],
            ),
            dcc.Dropdown(id="converter-dropdown", options=converters, value=converters[0]["value"] if converters else None, clearable=False),
            html.Div(id="param-controls", children=controls),
            html.Div(
                className="sim-controls",
                children=[
                    html.Button("▶ Run", id="run-btn", n_clicks=0),
                    html.Button("⏹ Stop", id="stop-btn", n_clicks=0),
                    html.Button("↺ Reset", id="reset-btn", n_clicks=0),
                ],
            ),
            dcc.Dropdown(
                id="export-dropdown",
                options=[
                    {"label": "PNG", "value": "png"},
                    {"label": "SVG", "value": "svg"},
                    {"label": "CSV", "value": "csv"},
                    {"label": "JSON", "value": "json"},
                ],
                placeholder="Export",
            ),
        ],
    )
