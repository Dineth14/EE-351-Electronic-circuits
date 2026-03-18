# Dashboard Integration Guide

**Purpose**: Help integrate newly created UI components into the dashboard callbacks and layout.

**Status**: New components created, ready for integration into existing dashboard structure.

---

## Files Created (Ready to Integrate)

### New Component Panels (power_electronics/dashboard/components/)

1. **theory_panel.py** (NEW)
   - Complete theory education module with circuit diagrams, equations, waveform sketches
   - Import: `from power_electronics.dashboard.components import theory_panel`
   - Usage: `theory_tab = theory_panel()`
   - No callbacks needed initially (static content can be populated per converter)

2. **Updated waveform_panel.py** (Upgraded)
   - Oscilloscope-grade UI with cursor measurements, signal math, time base controls
   - Import: `from power_electronics.dashboard.components import waveform_panel`
   - Callbacks needed:
     - `update-waveforms-graph`: Render based on `simulation-result-store`
     - `waveform-cycles-dropdown`: Change X-axis range (no re-sim needed)
     - `zoom-steady-state-btn`: Auto-detect settle time and zoom
     - `add-math-channel-btn`: Expand math channel dropdown
     - Cursor measurement: Use plotly shapes + `dcc.Store('cursor-positions')`

3. **Updated metrics_panel.py** (Upgraded)
   - Instrument-grade metrics with power flow, component stress, theory vs sim
   - Import: `from power_electronics.dashboard.components import metrics_panel`
   - Callbacks needed:
     - Populate all metric cards from `metrics` dict in `SimulationResult`
     - Create comparison table from `theoretical_values()` vs simulated
     - Color-code based on error % (<2%=green, 2-5%=yellow, >5%=red)

4. **Updated spectrum_panel.py** (Upgraded)
   - Dual-panel harmonic analysis with THD gauge and filter simulation
   - Import: `from power_electronics.dashboard.components import spectrum_panel`
   - Callbacks needed:
     - `spectrum-amplitude-graph`: FFT plot with selectable scale
     - `spectrum-phase-graph`: Phase angle plot
     - `thd-gauge-graph`: Circular gauge with color zones
     - `harmonic-table`: Populate from `harmonic_spectrum()`
     - `filter-sim-toggle-btn`: Show/hide filter simulation panel
     - `filter-l-slider`, `filter-c-slider`: Recalculate cutoff, replot

5. **Updated sidebar.py** (Upgraded)
   - Advanced parameter controls with presets, sweep mode, simulation settings
   - Import: `from power_electronics.dashboard.components import sidebar_layout`
   - Usage: `sidebar = sidebar_layout()` — returns complete sidebar
   - Callbacks needed:
     - Preset dropdown → populate all parameter sliders
     - Parameter sliders ↔ numeric inputs (bidirectional sync)
     - Sweep mode toggle → show/hide sweep controls
     - "Run Sweep" button → generate sweep results store
     - Theme selector → update `dcc.Store('theme-store')` + inject CSS variables
     - Export buttons → trigger `export.py` functions with current results

### New Export Module (power_electronics/dashboard/)

6. **export.py** (NEW)
   - PNG, SVG, CSV, JSON, PDF export functionality
   - Import: `from power_electronics.dashboard.export import export_png, export_csv, export_pdf, ...`
   - Usage examples:
     ```python
     # PNG
     png_bytes = export_png(waveform_figure, scale=3)
     
     # CSV
     csv_bytes = export_csv(simulation_result)
     
     # PDF Report
     pdf_bytes = export_report_pdf(
         result, 
         waveform_figure=waveform_graph,
         spectrum_figure=spectrum_graph
     )
     
     # Batch export all formats
     files = export_all_formats(result, "/output/dir", waveform_graph, spectrum_graph)
     ```

### Updated Theme System (power_electronics/visualization/)

7. **themes.py** (Upgraded)
   - 3 publication-quality themes: Oscilloscope, Dark Engineering, Light Paper
   - Import: `from power_electronics.visualization.themes import OSCILLOSCOPE, DARK_ENGINEERING, LIGHT_PAPER, get_theme`
   - Usage:
     ```python
     theme = get_theme('oscilloscope')
     plotly_template = theme.to_plotly_template()
     css_vars = theme.to_css_variables()  # For injection into page
     signal_colors = theme.signal_colors  # 12-color palette
     ```

### Enhanced Analysis (power_electronics/core/)

8. **analysis.py** (Upgraded)
   - 20+ signal analysis functions with comprehensive docstrings
   - Import: `from power_electronics.core.analysis import compute_thd, compute_ripple_voltage, ...`
   - New functions: `harmonic_spectrum()`, `compute_crest_factor()`, `compute_settling_time()`, etc.

---

## Integration Checklist

### 1. Dashboard Layout Update (dashboard/layout.py)

```python
# Import new components
from power_electronics.dashboard.components import (
    sidebar_layout,
    waveform_panel,
    metrics_panel,
    spectrum_panel,
    theory_panel,
)

# Add to main layout
app_layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='simulation-result-store'),  # Store simulation results
    dcc.Store(id='theme-store', data='oscilloscope'),  # Theme active
    dcc.Store(id='sweep-results-store'),  # Multi-parameter sweep results
    dcc.Store(id='cursor-positions'),  # Oscilloscope cursor measurements
    
    html.Div(style={'display': 'flex', 'height': '100vh'}, children=[
        sidebar_layout(),  # Left sidebar
        
        html.Div(style={'flex': 1, 'display': 'flex', 'flexDirection': 'column'}, children=[
            # Top menu bar
            html.Div([...export buttons, theme selector...]),
            
            # Main content area (4 tabs)
            dcc.Tabs(children=[
                dcc.Tab(label='Waveforms', children=[waveform_panel()]),
                dcc.Tab(label='Metrics', children=[metrics_panel()]),
                dcc.Tab(label='Spectrum', children=[spectrum_panel()]),
                dcc.Tab(label='Theory', children=[theory_panel()]),
            ]),
        ]),
    ]),
])
```

### 2. Callback Updates (dashboard/callbacks.py)

Key callbacks to implement/update:

```python
from dash import callback, Input, Output, State, ctx
from power_electronics.dashboard.export import (
    export_png, export_csv, export_json, export_report_pdf
)

# Theme switching
@callback(
    Output('app-root', 'style'),  # or use clientside
    Input('theme-store', 'data'),
)
def update_theme(theme_name):
    theme = get_theme(theme_name)
    css_vars = theme.to_css_variables()
    inline_style = {k[2:]: v for k, v in css_vars.items()}  # Strip '--'
    return inline_style

# Parameter preset selection
@callback(
    [Output({'type': 'param-slider', 'index': ALL}, 'value'),
     Output('preset-description', 'children')],
    Input('preset-dropdown', 'value'),
    prevent_initial_call=True,
)
def load_preset(preset_name):
    if preset_name == 'custom':
        return [no_update] * len(...), ''
    
    preset = PARAMETER_PRESETS[preset_name]
    values = [preset['params'].get(...) for ... in ...]
    description = preset['description']
    return values, description

# Simulation execution
@callback(
    Output('simulation-result-store', 'data'),
    Input('run-btn', 'n_clicks'),
    [State({'type': 'param-slider', 'index': ALL}, 'value'),
     State({'type': 'param-slider', 'index': ALL}, 'id'),
     State('converter-dropdown', 'value'),
     State('sim-time-dropdown', 'value'),
     State('points-per-cycle-radio', 'value'),
     State('solver-radio', 'value')],
    prevent_initial_call=True,
)
def run_simulation(n_clicks, param_values, param_ids, converter_key, ...):
    # Build params dict from slider values and IDs
    params = {id['index']: value for id, value in zip(param_ids, param_values)}
    
    # Instantiate converter
    converter = CONVERTER_REGISTRY[converter_key](**params)
    
    # Run simulation
    result = converter.simulate(t_end=..., num_points=...)
    
    # Return as JSON-serializable dict
    return {
        'converter_name': result.converter_name,
        'time': result.time.tolist(),
        'signals': {k: v.tolist() for k, v in result.signals.items()},
        'metrics': result.metrics,
        'params': result.params,
    }

# Waveform plot rendering
@callback(
    Output('waveform-graph', 'figure'),
    [Input('simulation-result-store', 'data'),
     Input('signal-selector-container', 'children'),
     Input('theme-store', 'data')],
    prevent_initial_call=True,
)
def update_waveforms(result_json, signal_checkboxes, theme_name):
    if not result_json:
        raise PreventUpdate
    
    theme = get_theme(theme_name)
    fig = go.Figure()
    
    # Plot selected signals
    for signal_name in selected_signals:
        time = np.array(result_json['time'])
        signal_data = np.array(result_json['signals'][signal_name])
        color = theme.signal_colors[signal_index % len(theme.signal_colors)]
        
        fig.add_trace(go.Scatter(x=time, y=signal_data, mode='lines',
                                 name=signal_name, line=dict(color=color)))
    
    fig.update_layout(
        template=theme.to_plotly_template(),
        hovermode='x unified',
        xaxis_title='Time (s)',
        yaxis_title='Amplitude',
    )
    return fig

# Spectrum plot rendering
@callback(
    Output('spectrum-amplitude-graph', 'figure'),
    [Input('simulation-result-store', 'data'),
     Input('spectrum-scale-radio', 'value'),
     Input('theme-store', 'data')],
    prevent_initial_call=True,
)
def update_spectrum(result_json, scale, theme_name):
    if not result_json:
        raise PreventUpdate
    
    theme = get_theme(theme_name)
    vout = np.array(result_json['signals']['V_out'])
    fs = len(result_json['time']) / (result_json['time'][-1] - result_json['time'][0])
    f0 = 50  # Fundamental (50 Hz or 60 Hz)
    
    freqs, mags = compute_fft(vout, fs)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=freqs, y=mags, marker_color=theme.accent_1))
    
    fig.update_layout(
        template=theme.to_plotly_template(),
        xaxis_title='Frequency (Hz)',
        yaxis_title=f'Amplitude ({scale})',
        title=f'Harmonic Spectrum (Scale: {scale})',
    )
    return fig

# Metrics update
@callback(
    [Output('metric-cards', 'children'),
     Output('comparison-table', 'data')],
    Input('simulation-result-store', 'data'),
    prevent_initial_call=True,
)
def update_metrics(result_json):
    if not result_json:
        raise PreventUpdate
    
    metrics = result_json['metrics']
    
    # Metric cards (primary)
    cards = [
        _metric_card('V_out', f"{metrics['V_out_avg']:.3f} V", ...),
        _metric_card('Efficiency', f"{metrics['efficiency']:.2f} %", ...),
        ...
    ]
    
    # Comparison table (theory vs sim)
    theory = converter.get_theoretical_values()
    table_data = [
        {
            'metric': 'V_out (avg)',
            'simulated': f"{metrics['V_out_avg']:.4f}",
            'theoretical': f"{theory['V_out']:.4f}",
            'error_pct': f"{abs(metrics['V_out_avg'] - theory['V_out']) / theory['V_out'] * 100:.2f}%",
            'status': '✓',
        },
        ...
    ]
    return cards, table_data

# PDF export
@callback(
    Output('download-pdf', 'data'),
    Input('export-pdf-btn', 'n_clicks'),
    [State('simulation-result-store', 'data'),
     State('waveform-graph', 'figure'),
     State('spectrum-amplitude-graph', 'figure')],
    prevent_initial_call=True,
)
def export_pdf(n_clicks, result_json, waveform_fig, spectrum_fig):
    if not result_json:
        raise PreventUpdate
    
    result = SimulationResult(
        time=np.array(result_json['time']),
        signals={k: np.array(v) for k, v in result_json['signals'].items()},
        metrics=result_json['metrics'],
        params=result_json['params'],
        converter_name=result_json['converter_name'],
    )
    
    waveform = go.Figure(waveform_fig) if waveform_fig else None
    spectrum = go.Figure(spectrum_fig) if spectrum_fig else None
    
    pdf_bytes = export_report_pdf(result, waveform, spectrum)
    
    return dict(
        content=pdf_bytes,
        filename=f"{result.converter_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        base64=False,
    )
```

### 3. CSS Stylesheet (assets/dashboard/style.css)

Update CSS to use theme variables:

```css
:root {
  /* Defaults (overridden by theme-store) */
  --bg-primary: #050a05;
  --bg-secondary: #0a140a;
  --bg-plot: #050a05;
  --grid-color: rgba(0,255,80,0.12);
  --text-primary: #00ff50;
  --text-secondary: #00aa35;
  --accent-1: #00ff50;
  --accent-2: #ffcc00;
  --accent-3: #ff5500;
  --good-color: #00ff50;
  --warn-color: #ffcc00;
  --danger-color: #ff3300;
}

body {
  background-color: var(--bg-primary);
  color: var(--text-primary);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.sidebar {
  background-color: var(--bg-primary);
  border-right: 1px solid var(--grid-color);
}

.metric-card {
  background-color: var(--bg-secondary);
  border: 1px solid var(--accent-1);
  border-radius: 4px;
  padding: 8px;
}

.primary-metrics-row {
  border-bottom: 1px solid var(--grid-color);
}

.waveform-panel {
  background-color: var(--bg-primary);
  display: flex;
  flex-direction: column;
  height: 100%;
}

.waveform-graph {
  flex: 1;
}

...
```

---

## Testing the Integration

### 1. Unit test callbacks in isolation

```bash
# Create test_callbacks.py in tests/
pytest tests/test_callbacks.py -v
```

### 2. Run dashboard locally

```bash
python -m power_electronics.dashboard.app
# Open http://localhost:8050
```

### 3. Test each panel:

- **Waveforms**: Select different signals, zoom, trigger, cursor measurement
- **Metrics**: Verify primary metrics + comparison table + power flow
- **Spectrum**: Check THD gauge, harmonic table, filter simulation toggle
- **Theory**: Verify equation tabs, waveform sketch (may need to generate)
- **Export**: Try PDF, CSV, PNG exports

### 4. Theme switching

- Click theme selector → verify colors update live
- Check that CSS variables are injected

---

## Known Limitations & TODOs

1. **Circuit Diagrams** (theory_panel.py):
   - Currently placeholder layout
   - Need to implement schemdraw generation → PNG conversion
   - Currently showing `data:image/png;base64,` placeholders

2. **Waveform Math Channels**:
   - UI created, callbacks not implemented
   - Need to add math operations (A+B, FFT, d/dt)

3. **Cursor Measurement**:
   - UI layout created with cursor readout panel
   - Need to implement plotly shapes + drag handlers

4. **Parameter Sweep Results**:
   - Sweep mode UI created
   - Need callback to generate 2D efficiency map + animated plot

5. **Filter Simulation**:
   - UI panel created
   - Need callback to apply IIR filter + replot

6. **Transient/Step Response Analysis**:
   - Tabs planned but not in components yet
   - Need to add to callbacks for advanced analysis

---

## References

- **Dash Documentation**: https://dash.plotly.com/
- **Plotly.js**: https://plotly.com/javascript/
- **CSS Variables**: https://developer.mozilla.org/en-US/docs/Web/CSS/--*

---

**Next Action**: Implement callbacks one panel at a time, starting with waveforms → metrics → spectrum → theory.
