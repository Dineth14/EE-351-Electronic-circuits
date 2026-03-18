"""Run a standalone buck converter simulation and print key metrics."""

from power_electronics.converters.dc_dc.buck import BuckConverter


def main() -> None:
    converter = BuckConverter(
        {
            "Vin": 48.0,
            "duty_cycle": 0.4,
            "frequency": 20000.0,
            "L": 1e-3,
            "C": 220e-6,
            "R_load": 15.0,
            "R_L": 0.05,
        }
    )
    result = converter.simulate(0.03, 8000)
    print("Buck simulation metrics:")
    for k, v in result.metrics.items():
        print(f"{k}: {v:.4f}")


if __name__ == "__main__":
    main()
