"""Waveform display panel component."""

from dash import dcc, html


def waveform_panel() -> html.Div:
    """Build waveform panel with signal selector and graph area."""
    return html.Div(
        className="panel waveform-panel",
        children=[
            dcc.Checklist(id="signal-selector", inline=True),
            dcc.Graph(id="waveform-graph", config={"displaylogo": False, "scrollZoom": True}),
        ],
    )
