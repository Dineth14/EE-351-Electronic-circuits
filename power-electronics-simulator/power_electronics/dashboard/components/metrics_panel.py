"""Metrics cards and comparison table panel."""

from dash import dash_table, html


def metrics_panel() -> html.Div:
    """Build metrics dashboard panel."""
    return html.Div(
        className="panel metrics-panel",
        children=[
            html.Div(id="metric-cards", className="metric-grid"),
            dash_table.DataTable(id="comparison-table", page_size=8, style_table={"overflowX": "auto"}),
        ],
    )
