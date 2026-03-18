"""Frequency spectrum panel component."""

from dash import dcc, html


def spectrum_panel() -> html.Div:
    """Build harmonic spectrum panel."""
    return html.Div(
        className="panel spectrum-panel",
        children=[
            dcc.Checklist(id="odd-only-toggle", options=[{"label": "Odd Harmonics Only", "value": "odd"}], value=[]),
            html.H3(id="thd-display", children="THD: -- %"),
            dcc.Graph(id="spectrum-graph", config={"displaylogo": False}),
        ],
    )
