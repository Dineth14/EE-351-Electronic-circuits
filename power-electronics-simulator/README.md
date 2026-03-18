# Power Electronics Simulator

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![CI](https://img.shields.io/github/actions/workflow/status/example/power-electronics-simulator/ci.yml)

```text
 ____                        _____ _           _                   _
|  _ \ _____      _____ _ __| ____| | ___  ___| |_ _ __ ___  _ __ | | ___  _   _
| |_) / _ \ \ /\ / / _ \ '__|  _| | |/ _ \/ __| __| '__/ _ \| '_ \| |/ _ \| | | |
|  __/ (_) \ V  V /  __/ |  | |___| |  __/ (__| |_| | | (_) | | | | | (_) | |_| |
|_|   \___/ \_/\_/ \___|_|  |_____|_|\___|\___|\__|_|  \___/|_| |_|_|\___/ \__, |
                                                                            |___/
```

High-fidelity educational and engineering simulation toolkit for AC-DC, DC-AC, and DC-DC converter systems.

## Features

| Category | Converter | Implemented |
|---|---|---|
| AC-DC | Half-wave rectifier | ✅ |
| AC-DC | Full-wave center-tap | ✅ |
| AC-DC | Full-bridge rectifier | ✅ |
| AC-DC | Three-phase half-wave (M3) | ✅ |
| AC-DC | Three-phase bridge (B6) | ✅ |
| AC-DC | SCR half-wave | ✅ |
| AC-DC | SCR full-bridge | ✅ |
| AC-DC | Vienna rectifier (simplified PFC) | ✅ |
| DC-DC | Buck | ✅ |
| DC-DC | Boost | ✅ |
| DC-DC | Buck-boost | ✅ |
| DC-DC | Cuk | ✅ |
| DC-DC | SEPIC | ✅ |
| DC-DC | Flyback | ✅ |
| DC-DC | Forward | ✅ |
| DC-DC | Dual active bridge | ✅ |
| DC-AC | Single-phase H-bridge VSI | ✅ |
| DC-AC | Three-phase VSI | ✅ |
| DC-AC | Push-pull inverter | ✅ |
| DC-AC | Cascaded H-bridge | ✅ |
| DC-AC | 3-level NPC inverter | ✅ |

## Quick Start

```bash
pip install -e ".[dev]"
python -m power_electronics.dashboard.app
```

## Demo

- Screenshot/GIF placeholder: add generated dashboard captures to docs/assets.

## Theory References

- Mohan, Undeland, Robbins - Power Electronics: Converters, Applications, and Design
- Rashid - Power Electronics Handbook

## Documentation

Build docs locally:

```bash
make docs
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This project is licensed under MIT. See [LICENSE](LICENSE).
