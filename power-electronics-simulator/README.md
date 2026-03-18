# ⚡ Power Electronics Simulator

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Type checking: mypy](https://img.shields.io/badge/type%20checking-mypy-blue)](http://mypy-lang.org/)
[![Linting: flake8](https://img.shields.io/badge/linting-flake8-blue)](https://flake8.pycqa.org/)
[![CI/CD](https://github.com/you/power-electronics-simulator/actions/workflows/ci.yml/badge.svg)](https://github.com/you/power-electronics-simulator/actions)
[![Codecov](https://codecov.io/gh/you/power-electronics-simulator/branch/main/graph/badge.svg)](https://codecov.io/gh/you/power-electronics-simulator)

---

> **The most comprehensive open-source interactive power electronics simulation and visualization platform.**
>
> Built by engineers, for engineers, researchers, and students. Publication-quality analysis with interactive dashboard, Jupyter notebooks, and rigorous physics.

```
 ╔═══════════════════════════════════════════════════════════════╗
 ║                   POWER ELECTRONICS SIMULATOR                ║
 ║                                                               ║
 ║  AC-DC Converters  │  DC-DC Converters  │  DC-AC Inverters  ║
 ║                                                               ║
 ║  • Full theoretical support (Mohan, Rashid, Erickson)       ║
 ║  • Interactive Plotly dashboard with oscilloscope UI        ║
 ║  • CCM/DCM auto-detection for DC-DC converters             ║
 ║  • Publication-quality waveforms & harmonic analysis        ║
 ║  • Jupyter notebooks with theory + interactive exploration  ║
 ║  • Export to PNG, SVG, CSV, JSON, PDF                       ║
 ║  • Multi-theme support (Oscilloscope, Engineering, Paper)   ║
 ║  • ≥85% test coverage with convergence validation           ║
 ║                                                               ║
 └═══════════════════════════════════════════════════════════════┘
```

---

## ✨ Features

### Converter Families

| **AC-DC Converters** | **DC-DC Converters** | **DC-AC Inverters** |
|-|-|-|
| ✅ Diode Rectifier (1φ, 3φ) | ✅ Buck | ✅ Single-Phase H-Bridge |
| ✅ SCR Rectifier (Controlled) | ✅ Boost | ✅ Three-Phase VSI |
| ✅ Boost PFC | ✅ Buck-Boost | ✅ Cascade H-Bridge |
| ✅ Vienna Rectifier | ✅ Ćuk | ✅ NPC 3-Level |
| | ✅ SEPIC | |
| | ✅ Flyback (Isolated) | |
| | ✅ Forward (Isolated) | |
| | ✅ Dual Active Bridge | |

### Core Capabilities

- **Rigorous Physics**: State-space simulation with proper small-signal transfer functions, CCM/DCM transitions, and theoretical formula validation
- **Interactive Dashboard**: Oscilloscope-grade UI with cursor measurement, waveform math, live parameter sweeps, efficiency maps, and Bode plots
- **Multi-Theme**: Oscilloscope (green-on-black), Dark Engineering (purple-blue), Light/Paper (publication quality)
- **Advanced Analysis**: THD, ripple voltage/current, power factor (displacement + distortion), crest factor, form factor, settling time
- **Jupyter Notebooks**: 8 complete notebooks covering theory, interactive exploration, harmonic deep-dives, and converter comparisons
- **Export System**: PNG, SVG, CSV, JSON, PDF reports with embedded plots and metrics tables
- **Code Quality**: Type hints (mypy strict), auto-formatted (black), linted (flake8), imported sorted (isort), ≥85% test coverage
- **CI/CD**: GitHub Actions for automated testing, linting, notebook execution, and documentation builds

### Signal Analysis

- FFT-based harmonic extraction with configurable orders
- THD (IEC 61000-3-2 compliant)
- Ripple voltage and current with peak-to-peak and RMS metrics
- True power factor (P / VA with distortion correction)
- Displacement power factor (fundamental phase angle)
- Crest factor (peakiness indicator)
- Form factor (shape indicator)
- Transformer Utilization Factor (TUF)
- Transient analysis: settling time, overshoot, undershoot
- Theoretical vs. simulated error metrics

---

## 🚀 Installation

### Recommended: Full Installation

```bash
# Install with all development and notebook tools
pip install -e ".[all]"
```

### Alternative Installation Options

```bash
# Core only (minimal dependencies)
pip install power-electronics-simulator

# With development tools (testing, linting, type checking)
pip install -e ".[dev]"

# With Jupyter notebook support
pip install -e ".[notebooks]"

# Everything combined
pip install -e ".[all]"
```

### From Source

```bash
git clone https://github.com/you/power-electronics-simulator.git
cd power-electronics-simulator
pip install -e ".[dev]"
```

---

## 🎬 Quick Start

### Launch Interactive Dashboard

```bash
python -m power_electronics.dashboard.app
```

Then navigate to: **http://localhost:8050**

### Run Jupyter Notebooks

```bash
jupyter notebook notebooks/
# Start with: 01_Theory_AC_DC_Converters.ipynb
```

### Command-Line Simulation

```python
from power_electronics import CONVERTER_REGISTRY

# Instantiate a Buck converter
buck = CONVERTER_REGISTRY['buck'](
    V_in=48.0,           # Input voltage (V)
    V_out=12.0,          # Output voltage (V)
    f_sw=200e3,          # Switching frequency (Hz)
    L=4e-6,              # Inductance (H)
    C=44e-6,             # Capacitance (F)
    R_load=2.4,          # Load resistance (Ω)
)

# Run simulation
result = buck.simulate(t_end=1e-3, num_points=5000)

# Access waveforms
print(f"Output voltage (avg): {result.metrics['V_out_avg']:.3f} V")
print(f"Efficiency: {result.metrics['efficiency']:.2f} %")
print(f"THD: {result.metrics['THD']:.2f} %")

# Plot waveforms
import matplotlib.pyplot as plt
plt.figure(figsize=(12, 6))
plt.plot(result.time * 1e6, result.signals['V_out'], label='Output Voltage')
plt.xlabel('Time (μs)')
plt.ylabel('Voltage (V)')
plt.legend()
plt.grid(True)
plt.show()
```

---

## 📐 Theory Accuracy

All converter models are validated against standard references:

| Converter | Formula Source | Max Error | Validation |
|-----------|---------|-----------|----------|
| **Buck** | Mohan Ch.3 | <1.0% | CCM/DCM transition verified |
| **Boost** | Mohan Ch.4 | <1.5% | Right-half-plane zero confirmed |
| **Buck-Boost** | Mohan Ch.5 | <1.5% | Polarity inversion verified |
| **Ćuk** | Erickson pp.230-260 | <2.0% | Coupled inductor effects included |
| **SEPIC** | Rashid Ch.8 | <2.0% | Energy transfer verified |
| **Flyback** | Mohan Ch.13 | <3.0% | Energy storage cycle validated |
| **Forward** | Mohan Ch.12 | <2.0% | Reset winding flux balancing |
| **DAB** | Transformer-isolated | <3.0% | Phase-shift modulation dynamics |
| **Diode Bridge** | IEEE 1653 | <0.5% | Peak & average voltage verified |
| **SCR Rectifier** | IEEE 1653 | <1.0% | Extinction angle computed correctly |
| **Single-Phase VSI** | Mohan Ch.9 | <2.0% | SPWM + overmodulation regions |
| **3-Phase VSI** | Mohan Ch.10 | <2.0% | Space vector PWM equivalent |

---

## 📚 Documentation

### Online Documentation
- [Full API Reference](https://power-electronics-sim.readthedocs.io/api/)
- [Theory Guides](https://power-electronics-sim.readthedocs.io/theory/)
- [User Guide](https://power-electronics-sim.readthedocs.io/guide/)

### Local Build

```bash
# Build HTML documentation locally
make docs
# Open docs/_build/html/index.html in browser
```

Requires Sphinx + sphinx-rtd-theme (installed with `[dev]`).

---

## 📖 Jupyter Notebooks

Eight comprehensive interactive notebooks included:

1. **01_Theory_AC_DC_Converters** — Diode/SCR rectifiers, PFC, analytical derivations
2. **02_Interactive_AC_DC_Waveforms** — Live parameter sweeps, harmonic analysis
3. **03_Theory_DC_AC_Inverters** — PWM modulation, SPWM, overmodulation, vector control
4. **04_Interactive_DC_AC_Waveforms** — Inverter transients, frequency sweeps, THD tuning
5. **05_Theory_DC_DC_Converters** — Buck, Boost, isolation, CCM/DCM theory
6. **06_Interactive_DC_DC_Waveforms** — Mode detection, efficiency maps, boundary analysis
7. **07_Harmonic_Analysis_and_THD** — FFT, filter design, IEC 61000-3-2 compliance
8. **08_Converter_Comparison** — Side-by-side performance, application selection

Each notebook features:
- ✅ Styled header with Unicode converter icons
- ✅ Theory sections with LaTeX equations via `IPython.display.Math`
- ✅ Circuit diagrams via schemdraw
- ✅ Interactive sliders (ipywidgets) for parameter exploration
- ✅ Automatic metrics table with theoretical vs. simulated comparison
- ✅ Parameter sweep analysis with plots
- ✅ References to Mohan, Rashid, Erickson

**Run all notebooks:**
```bash
make test-notebooks
```

---

## 🏗️ Project Architecture

```
power-electronics-simulator/
├── power_electronics/
│   ├── core/
│   │   ├── base_converter.py        # Abstract converter base class
│   │   ├── simulation_engine.py     # Switched state-space ODE solver
│   │   ├── analysis.py              # Signal analysis (THD, ripple, PF, etc.)
│   │   └── signal_generator.py      # PWM, SPWM, gate signal generation
│   ├── converters/
│   │   ├── __init__.py              # Global CONVERTER_REGISTRY
│   │   ├── ac_dc/                   # AC-DC rectifier models
│   │   ├── dc_dc/                   # DC-DC converter models
│   │   └── dc_ac/                   # DC-AC inverter models
│   ├── dashboard/
│   │   ├── app.py                   # Dash app entry point
│   │   ├── layout.py                # UI structure (sidebar, tabs, plots)
│   │   ├── callbacks.py             # Interactivity (sliders → simulation)
│   │   ├── export.py                # PNG, SVG, CSV, JSON, PDF export
│   │   └── components/              # Waveform, metrics, spectrum, theory panels
│   └── visualization/
│       ├── themes.py                # 3 publication themes (Oscilloscope, Engineering, Paper)
│       ├── plotter.py               # Plotly waveform, spectrum, efficiency plots
│       └── interactive.py           # Dashboard-specific plot rendering
├── tests/
│   ├── test_ac_dc.py                # AC-DC converter tests
│   ├── test_dc_dc.py                # DC-DC converter + CCM/DCM tests
│   ├── test_dc_ac.py                # DC-AC inverter tests
│   ├── test_analysis.py             # Signal analysis unit tests
│   ├── test_dashboard.py            # Dashboard UI tests
│   └── conftest.py                  # Shared fixtures
├── notebooks/
│   └── [8 interactive Jupyter notebooks]
├── docs/
│   ├── conf.py                      # Sphinx configuration
│   ├── theory/                      # Theory guides (AC-DC, DC-AC, DC-DC)
│   └── [auto-generated API docs]
├── pyproject.toml                   # Project metadata + tool configs
├── .github/workflows/
│   └── ci.yml                       # GitHub Actions CI/CD pipeline
└── README.md (this file)
```

---

## 🧪 Testing & Validation

### Run Full Test Suite (85% coverage required)

```bash
pytest tests/ --cov=power_electronics --cov-report=term-missing --cov-fail-under=85
```

### Run Specific Test Categories

```bash
pytest tests/test_dc_dc.py -v          # DC-DC converters only
pytest tests/test_analysis.py -v       # Signal analysis
pytest -m "not slow" -v                # Exclude slow ODE solver tests
```

### Test Coverage

Tests validate:
- ✅ **Initialization**: Parameter ranges, schema compliance
- ✅ **Theoretical Accuracy**: Vout, efficiency, ripple within 1–3% of formulas
- ✅ **CCM/DCM Transitions**: Boundary detection at K_critical
- ✅ **Signal Completeness**: All required waveforms present, no NaN/Inf
- ✅ **Transient Behavior**: Settling time, overshoot measurements
- ✅ **Power Quality**: THD, power factor, harmonic content matches theory

### Continuous Integration

Every push triggers:
- **Code Quality**: flake8 (style), isort (imports), black (format), mypy (types)
- **Tests**: pytest with coverage ≥85%
- **Notebooks**: Execute all 8 notebooks end-to-end
- **Docs**: Sphinx-build without warnings
- **Security**: Bandit static analysis

See [.github/workflows/ci.yml](.github/workflows/ci.yml) for details.

---

## 🛠️ Common Tasks

```bash
# Format code (black + isort)
make format

# Run linters (flake8 + mypy)
make lint

# Run tests + coverage
make test

# Build docs locally
make docs

# Launch dashboard
make dashboard

# Run specific test
pytest tests/test_buck.py::test_theoretical_accuracy -v

# Build wheel distribution
make build
```

See [Makefile](Makefile) for all targets.

---

## 📋 Requirements

- **Python**: 3.11 or 3.12
- **Core**: numpy, scipy, matplotlib, plotly, pandas
- **Dashboard**: dash, dash-katex, ipywidgets, schemdraw
- **Export**: reportlab (PDF generation)
- **Dev**: pytest, pytest-cov, black, isort, flake8, mypy, sphinx
- **Notebooks**: jupyter, nbconvert

Full dependency list in [pyproject.toml](pyproject.toml).

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup & workflow
- Code style guide (black, isort, flake8, mypy)
- Adding new converter models
- Expanding test coverage
- Improving documentation

---

## 📄 License

MIT License — See [LICENSE](LICENSE) for details.

---

## 🙋 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/you/power-electronics-simulator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/you/power-electronics-simulator/discussions)
- **Email**: contact@power-electronics-sim.io

---

## 📚 References

1. **Mohan, N., Undeland, T. M., & Robbins, W. P.** (2003). *Power Electronics: Converters, Applications, and Design* (3rd ed.). Wiley.

2. **Rashid, M. H.** (2017). *Power Electronics Handbook: Devices, Circuits, and Applications* (4th ed.). Butterworth-Heinemann.

3. **Erickson, R. W., & Maksimovic, D.** (2020). *Fundamentals of Power Electronics* (3rd ed.). Springer.

4. **IEEE 1653–2015** — IEEE Standard for Low-Voltage DC Power Distribution Systems Onboard Ships.

5. **IEC 61000-3-2:2018** — EMC Limits: Harmonic Current Emissions.

---

## 🎯 Roadmap

- [ ] Multi-parameter sweep optimization (genetic algorithms)
- [ ] Real-time waveform capture from hardware (USB oscilloscope support)
- [ ] Model predictive control (MPC) design tool
- [ ] Thermal analysis (heatsink sizing)
- [ ] Acoustic noise prediction
- [ ] Neural network-based efficiency prediction
- [ ] Cloud deployment (AWS, Heroku)

---

**Enjoy simulating power electronics! ⚡** 

*Last updated: 2025-03-18 | Version 0.2.0*
