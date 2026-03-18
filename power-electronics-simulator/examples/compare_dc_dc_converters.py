"""Compare key metrics for selected DC-DC converters."""

from power_electronics.converters.dc_dc.boost import BoostConverter
from power_electronics.converters.dc_dc.buck import BuckConverter
from power_electronics.converters.dc_dc.buck_boost import BuckBoostConverter


BASE = {
    "Vin": 48.0,
    "duty_cycle": 0.4,
    "frequency": 20000.0,
    "L": 1e-3,
    "C": 220e-6,
    "R_load": 15.0,
    "R_L": 0.05,
}


def main() -> None:
    models = {
        "buck": BuckConverter(BASE),
        "boost": BoostConverter(BASE),
        "buck_boost": BuckBoostConverter(BASE),
    }
    print("converter,Vout_avg,efficiency")
    for name, model in models.items():
        result = model.simulate(0.03, 6000)
        print(f"{name},{result.metrics['Vout_avg']:.3f},{result.metrics['efficiency_%']:.2f}")


if __name__ == "__main__":
    main()
