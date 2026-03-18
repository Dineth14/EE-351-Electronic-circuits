"""Dash callback registration for simulation, visualization, export, and theory pipeline.

Wires all dashboard interactions: converter selection, parameter controls,
simulation execution, waveform/metric/spectrum/theory updates, and data export.
"""

from __future__ import annotations

import base64
import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from dash import ALL, Input, Output, State, dcc, html, no_update
from dash.exceptions import PreventUpdate

from power_electronics.converters import CONVERTER_REGISTRY
from power_electronics.core.analysis import (
    compute_crest_factor,
    compute_form_factor,
    compute_individual_harmonic_distortion,
    compute_overshoot,
    compute_power_factor,
    compute_ripple,
    compute_rise_time,
    compute_rms,
    compute_settling_time,
    compute_thd,
    compute_thd_r,
)
from power_electronics.dashboard.components.sidebar import build_param_controls
from power_electronics.dashboard.export import (
    export_csv,
    export_figure_bytes,
    export_json,
    export_pdf_report,
)
from power_electronics.visualization.interactive import build_waveform_figure, spectrum_figure
from power_electronics.visualization.themes import get_theme


# ---------------------------------------------------------------------------
# Serialization helpers
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Callback registration
# ---------------------------------------------------------------------------

def register_callbacks(app):
    """Attach all dashboard callbacks to the provided Dash app."""

    # ── 1. Filter converters by category ───────────────────────────
    @app.callback(
        Output("converter-dropdown", "options"),
        Output("converter-dropdown", "value"),
        Input("category-tabs", "value"),
    )
    def filter_converters(category: str):
        def match(name: str) -> bool:
            if category == "DC-DC":
                return name in {
                    "buck", "boost", "buck_boost", "cuk", "sepic",
                    "flyback", "forward", "dual_active_bridge",
                }
            if category == "DC-AC":
                return name in {
                    "single_phase_hbridge", "three_phase_vsi", "push_pull",
                    "cascaded_hbridge", "npc_inverter",
                }
            return name in {
                "half_wave", "full_wave_centertap", "full_bridge",
                "three_phase_half", "three_phase_bridge",
                "scr_half_wave", "scr_full_bridge", "vienna_rectifier",
            }

        options = [{"label": k, "value": k} for k in CONVERTER_REGISTRY if match(k)]
        return options, options[0]["value"] if options else no_update

    # ── 2. Refresh parameter controls on converter change ──────────
    @app.callback(
        Output("param-controls", "children"),
        Input("converter-dropdown", "value"),
    )
    def refresh_params(converter_key: str):
        schema = CONVERTER_REGISTRY[converter_key].get_param_schema()
        return build_param_controls(schema)

    # ── 3. Run simulation ──────────────────────────────────────────
    @app.callback(
        Output("result-store", "data"),
        Output("history-store", "data"),
        Output("sim-status", "children"),
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
        row = {"converter": converter_key}
        for k, v in result.metrics.items():
            if isinstance(v, (int, float)):
                row[k] = round(v, 4)
        hist.append(row)
        status = f"✓ {converter_key} | {len(result.time)} pts | {len(result.signals)} signals"
        return payload, hist[-20:], status

    # ── 4. Update signal selector ──────────────────────────────────
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
        default_values = [o["value"] for o in opts[:min(6, len(opts))]]
        return opts, default_values

    # ── 5. Update waveform graph ───────────────────────────────────
    @app.callback(
        Output("waveform-graph", "figure"),
        Output("waveform-measurements", "children"),
        Input("result-store", "data"),
        Input("signal-selector", "value"),
        Input("theme-toggle", "value"),
    )
    def update_waveforms(data, selected, theme):
        if not data:
            raise PreventUpdate
        t, signals, _, _, _ = _from_serializable(data)
        fig = build_waveform_figure(t, signals, selected_signals=selected, theme=theme)

        # Measurement readout for first selected signal
        measurements = []
        for sig_name in (selected or [])[:3]:
            val = signals.get(sig_name, np.zeros(1))
            if val.ndim > 1:
                val = val[:, 0]
            rms = compute_rms(val)
            dc = float(np.mean(val))
            pp = float(np.max(val) - np.min(val))
            measurements.append(
                html.Span(f"{sig_name}: RMS={rms:.3f} DC={dc:.3f} PP={pp:.3f}")
            )
        return fig, measurements

    # ── 6. Update metrics cards + comparison table ─────────────────
    @app.callback(
        Output("metric-cards", "children"),
        Output("comparison-table", "data"),
        Output("power-flow-display", "children"),
        Output("efficiency-gauge", "figure"),
        Output("theory-vs-sim-table", "children"),
        Input("result-store", "data"),
        Input("history-store", "data"),
        Input("theme-toggle", "value"),
    )
    def update_metrics(data, history, theme):
        if not data:
            raise PreventUpdate
        t, signals, metrics, converter_name, params = _from_serializable(data)
        th = get_theme(theme)

        # ── KPI cards ──────────────────────────────────────────────
        cards = []
        card_defs = [
            ("Efficiency", "efficiency_%", "%", 90, 70),
            ("Vout Avg", "Vout_avg", "V", None, None),
            ("Vout Ripple", "Vout_ripple_%", "%", None, None),
            ("IL Ripple", "IL_ripple_A", "A", None, None),
            ("Input Power", "input_power_W", "W", None, None),
            ("Output Power", "output_power_W", "W", None, None),
        ]
        for label, key, unit, good_thresh, warn_thresh in card_defs:
            if key not in metrics:
                continue
            val = float(metrics[key])
            if good_thresh is not None:
                cls = "good" if val >= good_thresh else "warn" if val >= warn_thresh else "bad"
            else:
                cls = ""
            cards.append(
                html.Div(
                    className=f"metric-card {cls}",
                    children=[
                        html.H4(label, style={"fontSize": "10px", "margin": "0", "opacity": "0.7"}),
                        html.P(
                            f"{val:.3f} {unit}",
                            style={
                                "fontSize": "14px",
                                "fontWeight": "bold",
                                "margin": "4px 0 0 0",
                                "fontFamily": "'JetBrains Mono', monospace",
                            },
                        ),
                    ],
                )
            )

        # Add remaining metrics
        for key, value in metrics.items():
            if isinstance(value, str) or key in {d[1] for d in card_defs}:
                continue
            val = float(value)
            cls = "good" if val >= 90 else "warn" if val >= 50 else "bad"
            cards.append(
                html.Div(
                    className=f"metric-card {cls}",
                    children=[
                        html.H4(key, style={"fontSize": "10px", "margin": "0", "opacity": "0.7"}),
                        html.P(
                            f"{val:.4f}",
                            style={
                                "fontSize": "13px",
                                "fontWeight": "bold",
                                "margin": "4px 0 0 0",
                                "fontFamily": "'JetBrains Mono', monospace",
                            },
                        ),
                    ],
                )
            )

        # ── Power flow display ─────────────────────────────────────
        p_in = metrics.get("input_power_W", 0)
        p_out = metrics.get("output_power_W", 0)
        p_loss = max(0.0, p_in - p_out)
        eta = metrics.get("efficiency_%", 0)
        power_flow = html.Div(children=[
            html.Div("Power Flow", style={"fontWeight": "bold", "marginBottom": "6px", "color": th.colors.accent}),
            html.Div(f"Pin  = {p_in:.2f} W"),
            html.Div(f"Pout = {p_out:.2f} W"),
            html.Div(f"Ploss= {p_loss:.2f} W"),
            html.Div(f"η    = {eta:.1f} %", style={"color": th.colors.success, "fontWeight": "bold"}),
        ])

        # ── Efficiency gauge ───────────────────────────────────────
        gauge_fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=eta,
            number={"suffix": "%", "font": {"size": 28, "color": th.colors.font_color}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": th.colors.grid_color},
                "bar": {"color": th.colors.success if eta >= 85 else th.colors.warning},
                "bgcolor": th.colors.plot_bgcolor,
                "borderwidth": 1,
                "bordercolor": th.colors.border_color,
                "steps": [
                    {"range": [0, 70], "color": "rgba(255,60,60,0.15)"},
                    {"range": [70, 85], "color": "rgba(255,200,0,0.15)"},
                    {"range": [85, 100], "color": "rgba(0,255,100,0.15)"},
                ],
            },
        ))
        gauge_fig.update_layout(
            paper_bgcolor=th.colors.paper_bgcolor,
            font=dict(color=th.colors.font_color),
            height=170,
            margin=dict(l=30, r=30, t=20, b=10),
        )

        # ── Theory vs Simulation ───────────────────────────────────
        theory_vs = []
        try:
            converter = CONVERTER_REGISTRY[converter_name](params)
            theo = converter.get_theoretical_values()
            rows = []
            for k, tv in theo.items():
                sv = metrics.get(k, None)
                if sv is not None:
                    error = abs(sv - tv) / max(abs(tv), 1e-12) * 100
                    color = th.colors.success if error < 5 else th.colors.warning if error < 15 else th.colors.danger
                    rows.append(
                        html.Tr(children=[
                            html.Td(k, style={"padding": "3px 8px"}),
                            html.Td(f"{tv:.4f}", style={"padding": "3px 8px"}),
                            html.Td(f"{sv:.4f}", style={"padding": "3px 8px"}),
                            html.Td(f"{error:.2f}%", style={"padding": "3px 8px", "color": color}),
                        ])
                    )
            if rows:
                theory_vs = html.Table(
                    style={"width": "100%", "fontSize": "10px", "fontFamily": "'JetBrains Mono', monospace"},
                    children=[
                        html.Thead(html.Tr([
                            html.Th("Metric"), html.Th("Theory"), html.Th("Simulated"), html.Th("Error"),
                        ])),
                        html.Tbody(rows),
                    ],
                )
        except Exception:
            theory_vs = html.P("Theory comparison unavailable", style={"fontSize": "10px"})

        return cards, history or [], power_flow, gauge_fig, theory_vs

    # ── 7. Update spectrum + THD ───────────────────────────────────
    @app.callback(
        Output("spectrum-graph", "figure"),
        Output("thd-display", "children"),
        Output("thd-r-display", "children"),
        Output("ihd-table", "children"),
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

        fig, thd = spectrum_figure(
            target, fs, f0,
            odd_only=("odd" in (odd_values or [])),
            theme=theme,
        )
        thd_r = compute_thd_r(target, f0, fs)

        # Individual harmonic distortion cells
        ihd = compute_individual_harmonic_distortion(target, f0, fs, max_harmonic=15)
        ihd_cells = []
        for order, pct in ihd.items():
            color = "var(--accent, #00ff88)" if order == 1 else "var(--muted, #7a8ca5)"
            ihd_cells.append(
                html.Div(
                    style={"padding": "2px 4px", "textAlign": "center"},
                    children=[
                        html.Div(f"H{order}", style={"fontWeight": "bold", "color": color}),
                        html.Div(f"{pct:.1f}%"),
                    ],
                )
            )

        return fig, f"THD-F: {thd:.2f}%", f"THD-R: {thd_r:.2f}%", ihd_cells

    # ── 8. Update theory panel ─────────────────────────────────────
    @app.callback(
        Output("theory-title", "children"),
        Output("theory-description", "children"),
        Output("theory-category-badge", "children"),
        Output("theory-equations", "children"),
        Output("theory-circuit-img", "src"),
        Output("theory-reference-values", "children"),
        Output("theory-boundary-info", "children"),
        Input("converter-dropdown", "value"),
        Input("result-store", "data"),
    )
    def update_theory(converter_key, data):
        converter_cls = CONVERTER_REGISTRY[converter_key]
        info = converter_cls.get_info()

        # Equations rendered as KaTeX
        equations = html.Ul(
            style={"listStyle": "none", "padding": "0", "margin": "0"},
            children=[
                html.Li(
                    dcc.Markdown(f"$$ {eq} $$"),
                    style={"padding": "4px 0"},
                )
                for eq in info.equations
            ],
        )

        # Operating waveform diagram
        fig, ax = plt.subplots(figsize=(5, 2.5))
        ax.set_facecolor("#07090d")
        fig.patch.set_facecolor("#050508")
        t_demo = np.linspace(0, 4, 500)
        ax.plot(t_demo, np.sin(2 * np.pi * t_demo / 2), color="#00ff88", linewidth=1.5, label="Reference")
        ax.plot(t_demo, np.abs(np.sin(2 * np.pi * t_demo / 2)), color="#00ccff", linewidth=1.2, alpha=0.7, label="Output")
        ax.set_title(f"{info.name} — Operating Waveform", color="#9ef5c8", fontsize=10)
        ax.set_xlabel("t / T", color="#5a8a6e", fontsize=9)
        ax.set_ylabel("Normalized", color="#5a8a6e", fontsize=9)
        ax.tick_params(colors="#5a8a6e", labelsize=8)
        ax.grid(True, alpha=0.2, color="#133126")
        ax.legend(fontsize=8, facecolor="#0a0a0f", edgecolor="#133126", labelcolor="#9ef5c8")
        buffer = io.BytesIO()
        fig.tight_layout()
        fig.savefig(buffer, format="png", dpi=150, facecolor="#050508")
        plt.close(fig)
        encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
        img_src = f"data:image/png;base64,{encoded}"

        # Theoretical reference values
        ref_cells = []
        try:
            params = data.get("params", {}) if data else {}
            converter = converter_cls(params) if params else converter_cls({})
            theo = converter.get_theoretical_values()
            for k, v in theo.items():
                ref_cells.append(
                    html.Div(
                        style={
                            "padding": "4px 8px",
                            "borderRadius": "3px",
                            "background": "var(--bg-panel, #11131a)",
                            "border": "1px solid var(--grid-color, #26344c)",
                        },
                        children=[
                            html.Div(k, style={"fontSize": "9px", "opacity": "0.6"}),
                            html.Div(f"{v:.4f}", style={"fontWeight": "bold"}),
                        ],
                    )
                )
        except Exception:
            ref_cells = [html.P("Set parameters and run simulation for theoretical values.")]

        # CCM/DCM boundary
        boundary = html.Div(children=[
            dcc.Markdown(
                r"$$ I_{L,boundary} = \frac{(1-D) \cdot R}{2 \cdot L \cdot f_s} $$"
            ),
            html.P(
                "If average inductor current falls below this boundary, the converter "
                "enters Discontinuous Conduction Mode (DCM).",
                style={"fontSize": "10px", "color": "var(--muted, #7a8ca5)"},
            ),
        ])

        return (
            info.name,
            info.description,
            info.category,
            equations,
            img_src,
            ref_cells,
            boundary,
        )

    # ── 9. Export: CSV ─────────────────────────────────────────────
    @app.callback(
        Output("export-download", "data", allow_duplicate=True),
        Input("export-csv-btn", "n_clicks"),
        State("result-store", "data"),
        prevent_initial_call=True,
    )
    def do_export_csv(n_clicks, data):
        if not data or not n_clicks:
            raise PreventUpdate
        t, signals, metrics, name, params = _from_serializable(data)
        content = export_csv(t, signals, metrics, name)
        return dcc.send_string(content, filename=f"{name}_simulation.csv")

    # ── 10. Export: JSON ───────────────────────────────────────────
    @app.callback(
        Output("export-download", "data", allow_duplicate=True),
        Input("export-json-btn", "n_clicks"),
        State("result-store", "data"),
        prevent_initial_call=True,
    )
    def do_export_json(n_clicks, data):
        if not data or not n_clicks:
            raise PreventUpdate
        t, signals, metrics, name, params = _from_serializable(data)
        content = export_json(t, signals, metrics, name, params)
        return dcc.send_string(content, filename=f"{name}_simulation.json")

    # ── 11. Export: PNG ────────────────────────────────────────────
    @app.callback(
        Output("export-download", "data", allow_duplicate=True),
        Input("export-png-btn", "n_clicks"),
        State("result-store", "data"),
        State("signal-selector", "value"),
        prevent_initial_call=True,
    )
    def do_export_png(n_clicks, data, selected):
        if not data or not n_clicks:
            raise PreventUpdate
        t, signals, _, name, _ = _from_serializable(data)
        img_bytes = export_figure_bytes(t, signals, selected, fmt="png", title=f"{name} Waveforms")
        return dcc.send_bytes(img_bytes, filename=f"{name}_waveforms.png")

    # ── 12. Export: PDF ────────────────────────────────────────────
    @app.callback(
        Output("export-download", "data", allow_duplicate=True),
        Input("export-pdf-btn", "n_clicks"),
        State("result-store", "data"),
        State("signal-selector", "value"),
        prevent_initial_call=True,
    )
    def do_export_pdf(n_clicks, data, selected):
        if not data or not n_clicks:
            raise PreventUpdate
        t, signals, metrics, name, params = _from_serializable(data)
        pdf_bytes = export_pdf_report(t, signals, metrics, name, params, selected)
        return dcc.send_bytes(pdf_bytes, filename=f"{name}_report.pdf")
