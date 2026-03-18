"""Oscilloscope-grade waveform display panel.

Features:
  - Signal selection with color swatches
  - Multi-trace display with cursor measurement
  - Waveform math (A+B, A-B, FFT, derivatives)
  - Statistics per signal
  - Time base controls (cycles, zoom, trigger)
"""

from dash import dcc, html
import dash_colorpicker


def waveform_panel() -> html.Div:
    """Build oscilloscope-grade waveform panel.

    Returns
    -------
    html.Div
        Complete waveform panel with signal selector, main plot, cursors,
        statistics, and time base controls.
    """
    return html.Div(
        className="waveform-panel",
        children=[
            # Top control bar
            html.Div(
                className=" waveform-top-controls",
                children=[
                    html.Label("Time Base:", style={"font-weight": "bold"}),
                    dcc.Dropdown(
                        id="waveform-cycles-dropdown",
                        options=[
                            {"label": f"{c} cycles", "value": c}
                            for c in [1, 2,5, 10, 20]
                        ],
                        value=5,
                        style={"width": "120px", "marginRight": "20px"},
                    ),
                    html.Button(
                        "Zoom to Steady State",
                        id="zoom-steady-state-btn",
                        n_clicks=0,
                        style={
                            "padding": "6px 12px",
                            "marginRight": "20px",
                            "cursor": "pointer",
                        },
                    ),
                    html.Button(
                        "Add Math Channel",
                        id="add-math-channel-btn",
                        n_clicks=0,
                        style={"padding": "6px 12px", "cursor": "pointer"},
                    ),
                ],
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "marginBottom": "12px",
                    "padding": "8px",
                    "borderBottom": "1px solid var(--grid-color)",
                },
            ),
            # Signal selector panel (left side)
            html.Div(
                className="waveform-selector-panel",
                children=[
                    html.Div(
                        [
                            html.Label("Signals", style={"font-weight": "bold"}),
                            html.Div(
                                id="signal-selector-container",
                                className="signal-selector-list",
                            ),
                        ],
                        style={
                            "padding": "8px",
                            "borderRight": "1px solid var(--grid-color)",
                            "maxHeight": "500px",
                            "overflowY": "auto",
                        },
                    ),
                ],
                style={"flex": "0 0 180px"},
            ),
            # Main waveform plot (with cursors)
            html.Div(
                children=[
                    dcc.Graph(
                        id="waveform-graph",
                        config={
                            "displaylogo": False,
                            "displayModeBar": True,
                            "scrollZoom": True,
                            "responsive": True,
                        },
                        style={"height": "400px"},
                    ),
                    # Cursor readout
                    html.Div(
                        id="cursor-readout",
                        className="cursor-readout-panel",
                        style={
                            "padding": "8px",
                            "backgroundColor": "var(--bg-secondary)",
                            "fontSize": "12px",
                            "fontFamily": "monospace",
                            "borderTop": "1px solid var(--grid-color)",
                        },
                    ),
                ],
                style={"flex": "1", "display": "flex", "flexDirection": "column"},
            ),
        ],
        style={
            "display": "flex",
            "flexDirection": "column",
            "height": "100%",
            "padding": "8px",
            "backgroundColor": "var(--bg-primary)",
        },
    )


def create_signal_selector_item(signal_name: str, color: str) -> html.Div:
    """Create a single signal selector checkbox with color swatch.

    Parameters
    ----------
    signal_name:
        Name of the signal (e.g., 'V_out', 'I_L').
    color:
        Hex color code for signal trace.

    Returns
    -------
    html.Div
        Selector item with checkbox and color swatch.
    """
    return html.Div(
        children=[
            dcc.Checklist(
                id={"type": "signal-checkbox", "index": signal_name},
                options=[{"label": "", "value": signal_name}],
                value=[signal_name],
                style={"display": "inline-block", "marginRight": "4px"},
            ),
            html.Div(
                style={
                    "display": "inline-block",
                    "width": "12px",
                    "height": "12px",
                    "backgroundColor": color,
                    "border": "1px solid var(--text-secondary)",
                    "borderRadius": "2px",
                    "marginRight": "6px",
                    "cursor": "pointer",
                },
                title="Click to change color",
                id={"type": "color-swatch", "index": signal_name},
            ),
            html.Span(signal_name, style={"fontSize": "11px"}),
        ],
        style={
            "padding": "4px",
            "display": "flex",
            "alignItems": "center",
            "marginBottom": "4px",
        },
    )

