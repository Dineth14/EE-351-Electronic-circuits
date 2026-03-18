"""Run a full-bridge rectifier simulation."""

from power_electronics.converters.ac_dc.full_bridge import FullBridgeRectifier


def main() -> None:
    converter = FullBridgeRectifier(
        {
            "Vac_peak": 170.0,
            "frequency": 50.0,
            "R_load": 25.0,
            "L_filter": 1e-3,
            "C_filter": 2e-3,
        }
    )
    result = converter.simulate(0.15, 5000)
    print("Full-bridge rectifier metrics:")
    for k, v in result.metrics.items():
        print(f"{k}: {v:.4f}")


if __name__ == "__main__":
    main()
