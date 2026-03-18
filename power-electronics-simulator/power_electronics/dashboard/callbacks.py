"""Dash callback registration for simulation and plotting pipeline."""

from __future__ import annotations

import base64
import io

import matplotlib.pyplot as plt
import numpy as np
from dash import ALL, Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

from power_electronics.converters import CONVERTER_REGISTRY
from power_electronics.dashboard.components.sidebar import build_param_controls
from power_electronics.visualization.interactive import build_waveform_figure, spectrum_figure


def _to_serializable(result) -> dict:
    return {
        "time": result.time.tolist(),
        "signals": {k: np.asarray(v).tolist() for k, v in result.signals.items()},
        "metrics": result.metrics,
        "converter_name": result.converter_name,
        "params": result.params,
    }


def _from_serializable(payload: dict):
    time = np.array(payload["time"])
    signals = {k: np.array(v) for k, v in payload["signals"].items()}
    return time, signals, payload["metrics"], payload["converter_name"], payload["params"]


def register_callbacks(app):
    """Attach all dashboard callbacks to the provided Dash app."""

    @app.callback(
        Output("converter-dropdown", "options"),
        Output("converter-dropdown", "value"),
        Input("category-tabs", "value"),
    )
    def filter_converters(category: str):
        def match(name: str) -> bool:
            if category == "DC-DC":
                return name in {"buck", "boost", "buck_boost", "cuk", "sepic", "flyback", "forward", "dual_active_bridge"}
            if category == "DC-AC":
                return name in {"single_phase_hbridge", "three_phase_vsi", "push_pull", "cascaded_hbridge", "npc_inverter"}
            return name in {"half_wave", "full_wave_centertap", "full_bridge", "three_phase_half", "three_phase_bridge", "scr_half_wave", "scr_full_bridge", "vienna_rectifier"}

        options = [{"label": k, "value": k} for k in CONVERTER_REGISTRY if match(k)]
        return options, options[0]["value"]

    @app.callback(
        Output("param-controls", "children"),
        Input("converter-dropdown", "value"),
    )
    def refresh_params(converter_key: str):
        schema = CONVERTER_REGISTRY[converter_key].get_param_schema()
        return build_param_controls(schema)

    @app.callback(
        Output("result-store", "data"),
        Output("history-store", "data"),
        Input("run-btn", "n_clicks"),
        State("converter-dropdown", "value"),
        State({"type": "param-input", "name": ALL}, "id"),
        State({"type": "param-input", "name": ALL}, "value"),
        State("history-store", "data"),
        prevent_initial_call=True,
    )
    def run_simulation(_n_clicks, converter_key, input_ids, input_values, history):
        params = {}
        for item, value in zip(input_ids, input_values):
            key = item["name"]
            params[key] = value
        converter = CONVERTER_REGISTRY[converter_key](params)
        result = converter.simulate(t_end=0.1, num_points=4000)
        payload = _to_serializable(result)
        hist = list(history or [])
        hist.append({"converter": converter_key, **result.metrics})
        return payload, hist[-10:]

    @app.callback(
        Output("signal-selector", "options"),
        Output("signal-selector", "value"),
        Input("result-store", "data"),
    )
    def update_signal_selector(data):
        if not data:
            raise PreventUpdate
        _, signals, _, _, _ = _from_serializable(data)
        opts = [{"label": k, "value": k} for k in signals.keys()]
        default_values = [o["value"] for o in opts[: min(6, len(opts))]]
        return opts, default_values

    @app.callback(
        Output("waveform-graph", "figure"),
        Input("result-store", "data"),
        Input("signal-selector", "value"),
        Input("theme-toggle", "value"),
    )
    def update_waveforms(data, selected, theme):
        if not data:
            raise PreventUpdate
        t, signals, _, _, _ = _from_serializable(data)
        return build_waveform_figure(t, signals, selected_signals=selected, theme=theme)

    @app.callback(
        Output("metric-cards", "children"),
        Output("comparison-table", "data"),
        Input("result-store", "data"),
        Input("history-store", "data"),
    )
    def update_metrics(data, history):
        if not data:
            raise PreventUpdate
        _, _, metrics, _, _ = _from_serializable(data)
        cards = []
        for key, value in metrics.items():
            if isinstance(value, str):
                continue
            val = float(value)
            cls = "good" if val >= 90 else "warn" if val >= 50 else "bad"
            cards.append(html.Div(className=f"metric-card {cls}", children=[html.H4(key), html.P(f"{val:.3f}")]))
        return cards, history or []

    @app.callback(
        Output("spectrum-graph", "figure"),
        Output("thd-display", "children"),
        Input("result-store", "data"),
        Input("odd-only-toggle", "value"),
        Input("theme-toggle", "value"),
    )
    def update_spectrum(data, odd_values, theme):
        if not data:
            raise PreventUpdate
        t, signals, _, _, params = _from_serializable(data)
        target = signals.get("Vout", next(iter(signals.values())))
        if target.ndim > 1:
            target = target[:, 0]
        fs = 1.0 / (t[1] - t[0])
        f0 = float(params.get("f_output", params.get("frequency", 50.0)))
        fig, thd = spectrum_figure(target, fs, f0, odd_only=("odd" in (odd_values or [])), theme=theme)
        return fig, f"THD: {thd:.2f} %"

    @app.callback(
        Output("theory-panel", "children"),
        Input("converter-dropdown", "value"),
        Input("result-store", "data"),
    )
    def update_theory(converter_key, data):
        converter_cls = CONVERTER_REGISTRY[converter_key]
        info = converter_cls.get_info()
        equations = [html.Li(dcc.Markdown(f"$$ {eq} $$")) for eq in info.equations]
        fig, ax = plt.subplots(figsize=(4, 2.2))
        ax.plot([0, 1, 2, 3], [0, 1, 0, 1], color="#00ff88")
        ax.set_title("Operating Waveform")
        ax.set_xlabel("t")
        ax.set_ylabel("norm")
        ax.grid(True, alpha=0.3)
        buffer = io.BytesIO()
        fig.tight_layout()
        fig.savefig(buffer, format="png", dpi=130)
        plt.close(fig)
        encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
        boundary = r"I_{L,boundary}=\\frac{(1-D)R}{2Lf_s}"
        return html.Div(
            children=[
                html.H3(info.name),
                html.P(info.description),
                html.H4("Key Equations"),
                html.Ul(equations),
                html.H4("Operating Diagram"),
                html.Img(src=f"data:image/png;base64,{encoded}", style={"maxWidth": "420px", "border": "1px solid #203"}),
                html.H4("CCM/DCM Boundary"),
                dcc.Markdown(f"$$ {boundary} $$"),
            ]
        )
