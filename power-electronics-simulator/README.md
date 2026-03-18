# Power Electronics Simulator v2.0

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Tests](https://img.shields.io/badge/tests-187%20passing-brightgreen)

```text
 ____                        _____ _           _                   _
|  _ \ _____      _____ _ __| ____| | ___  ___| |_ _ __ ___  _ __ | | ___  _   _
| |_) / _ \ \ /\ / / _ \ '__|  _| | |/ _ \/ __| __| '__/ _ \| '_ \| |/ _ \| | | |
|  __/ (_) \ V  V /  __/ |  | |___| |  __/ (__| |_| | | (_) | | | | | (_) | |_| |
|_|   \___/ \_/\_/ \___|_|  |_____|_|\___|\___|\__|_|  \___/|_| |_|_|\___/ \__, |
                                                                            |___/
```

Publication-quality educational and engineering simulation toolkit for **AC-DC**, **DC-AC**, and **DC-DC** power converter systems. Features an oscilloscope-grade Dash dashboard, 22 converter models, 20+ analysis functions, multi-format export, and 187 passing tests.

---

## Highlights

- **22 converter models** across 3 families — every topology simulated with ODE-based time-domain solvers
- **Oscilloscope-grade dashboard** with waveform, spectrum, metrics, and theory panels
- **3 color themes** — Oscilloscope (phosphor green), Dark, and Light
- **20+ analysis functions** — FFT, THD, THD-R, PSD, crest/form factor, power triangle, Bode response, transient metrics
- **Multi-format export** — CSV, JSON, PNG, SVG, and multi-page PDF reports
- **187 tests** covering all converters, core analysis, simulation engine, export, and themes
- **8 Jupyter notebooks** with interactive widgets for parametric exploration

---

## Converters

| Category | Converter | Key |
|----------|-----------|-----|
| **AC-DC** | Half-wave rectifier | `half_wave` |
| | Full-wave center-tap | `full_wave_centertap` |
| | Full-bridge rectifier | `full_bridge` |
| | Three-phase half-wave (M3) | `three_phase_half` |
| | Three-phase bridge (B6) | `three_phase_bridge` |
| | SCR half-wave | `scr_half_wave` |
| | SCR full-bridge | `scr_full_bridge` |
| | Vienna rectifier (PFC) | `vienna_rectifier` |
| **DC-DC** | Buck | `buck` |
| | Boost | `boost` |
| | Buck-boost | `buck_boost` |
| | Cuk | `cuk` |
| | SEPIC | `sepic` |
| | Flyback | `flyback` |
| | Forward | `forward` |
| | Dual active bridge | `dual_active_bridge` |
| **DC-AC** | Single-phase H-bridge VSI | `single_phase_hbridge` |
| | Three-phase VSI | `three_phase_vsi` |
| | Push-pull inverter | `push_pull` |
| | Cascaded H-bridge | `cascaded_hbridge` |
| | 3-level NPC inverter | `npc_inverter` |

---

## Quick Start

```bash
# Install (editable with dev dependencies)
pip install -e ".[dev]"

# Launch dashboard
python -m power_electronics.dashboard.app
# or
power-sim
```

Open [http://127.0.0.1:8050](http://127.0.0.1:8050) in your browser.

### Python API

```python
from power_electronics.converters import CONVERTER_REGISTRY

# Instantiate and simulate
buck = CONVERTER_REGISTRY["buck"]({"Vin": 48, "duty_cycle": 0.5,
    "frequency": 20000, "L": 1e-3, "C": 220e-6, "R_load": 10, "R_L": 0.05})
result = buck.simulate(t_end=0.05, num_points=8000)

print(f"Vout avg: {result.metrics['Vout_avg']:.2f} V")
print(f"Efficiency: {result.metrics['efficiency_%']:.1f}%")
```

### Analysis

```python
from power_electronics.core.analysis import compute_full_analysis

metrics = compute_full_analysis(result.time, result.signals["Vout"],
                                 result.signals["IL"], f0=20000)
print(metrics)
```

---

## Dashboard

The Dash dashboard provides 4 tabbed panels:

| Tab | Features |
|-----|----------|
| **Waveforms** | ScatterGL rendering, signal selector, RMS/DC/PP measurements, drawing tools |
| **Metrics** | KPI cards, DataTable with sort/filter, power-flow display, efficiency gauge |
| **Spectrum** | Harmonic bar chart, THD-F and THD-R readouts, individual harmonic distortion table |
| **Theory** | LaTeX equations (via KaTeX), category badge, reference values, CCM/DCM boundary info |

**Additional features:**
- Grouped parameter controls (Voltage, Frequency, Control, Passives, Load, Transformer)
- Export buttons: CSV, JSON, PNG, PDF
- Theme selector: Oscilloscope, Dark, Light
- Simulation status indicator

---

## Analysis Functions

| Function | Description |
|----------|-------------|
| `compute_fft` | Windowed FFT magnitude spectrum |
| `compute_fft_phase` | FFT magnitude + phase |
| `compute_psd` | Welch power spectral density |
| `compute_thd` | Total harmonic distortion (THD-F) |
| `compute_thd_r` | THD relative to total RMS (THD-R) |
| `compute_harmonic_spectrum` | Per-harmonic amplitudes |
| `compute_rms`, `compute_mean`, `compute_peak_to_peak` | Basic measurements |
| `compute_crest_factor`, `compute_form_factor` | Waveform shape factors |
| `compute_ripple`, `compute_ripple_pp`, `compute_ripple_frequency` | Ripple analysis |
| `compute_efficiency`, `compute_power_factor` | Power metrics |
| `compute_power_triangle` | P, Q, S, PF decomposition |
| `compute_settling_time`, `compute_overshoot`, `compute_rise_time` | Transient metrics |
| `compute_component_stress` | V/I peak, RMS, average for component selection |
| `compute_bode_response` | Frequency response from transfer function coefficients |
| `compute_full_analysis` | All-in-one comprehensive metrics |

---

## Notebooks

| # | Notebook | Content |
|---|----------|---------|
| 01 | Theory: AC-DC Converters | Circuit diagrams, equations, efficiency curves |
| 02 | Interactive AC-DC Waveforms | ipywidgets parametric exploration |
| 03 | Theory: DC-AC Inverters | H-bridge schematics, THD equations |
| 04 | Interactive DC-AC Waveforms | SPWM modulation sweeps |
| 05 | Theory: DC-DC Converters | Steady-state equations, CCM/DCM |
| 06 | Interactive DC-DC Waveforms | Duty/frequency/load sweeps |
| 07 | Harmonic Analysis & THD | FFT, capacitor vs THD sweeps |
| 08 | Converter Comparison | Multi-converter efficiency/ripple radar charts |

---

## Testing

```bash
# Run all 187 tests
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=power_electronics --cov-report=term-missing
```

---

## Project Structure

```text
power-electronics-simulator/
├── power_electronics/
│   ├── core/
│   │   ├── analysis.py          # 20+ analysis functions
│   │   ├── base_converter.py    # ABC + dataclasses
│   │   ├── simulation_engine.py # ODE solver, PWM, SCR pulse generation
│   │   └── signal_generator.py  # SPWM generator
│   ├── converters/
│   │   ├── ac_dc/               # 8 rectifier models
│   │   ├── dc_dc/               # 8 chopper models
│   │   └── dc_ac/               # 5 inverter models
│   ├── dashboard/
│   │   ├── app.py               # Dash application factory
│   │   ├── layout.py            # 4-tab layout builder
│   │   ├── callbacks.py         # 12 reactive callbacks
│   │   ├── export.py            # CSV, JSON, PNG, SVG, PDF export
│   │   └── components/          # Sidebar + 4 panel components
│   └── visualization/
│       ├── themes.py            # Dataclass-based 3-theme system
│       ├── interactive.py       # 5 Plotly figure builders
│       └── plotter.py           # Matplotlib helper
├── notebooks/                   # 8 Jupyter notebooks
├── tests/                       # 187 tests
├── assets/dashboard/style.css   # Production CSS
├── docs/                        # Sphinx documentation source
└── pyproject.toml               # Project config (v2.0)
```

---

## Dependencies

- **Runtime:** numpy, scipy, matplotlib, plotly, dash, dash-katex, pandas, schemdraw, ipywidgets, reportlab
- **Dev:** pytest, pytest-cov, black, isort, mypy, ruff, bandit
- **Docs:** sphinx, sphinx-autodoc-typehints, myst-parser

---

## Theory References

- Mohan, Undeland, Robbins — *Power Electronics: Converters, Applications, and Design*
- Rashid — *Power Electronics Handbook*
- Hart — *Power Electronics*

## License

MIT — see [LICENSE](LICENSE).
