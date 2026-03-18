"""Run a single-phase SPWM inverter simulation."""

from power_electronics.converters.dc_ac.single_phase_hbridge import SinglePhaseHBridgeVSI


def main() -> None:
    converter = SinglePhaseHBridgeVSI(
        {
            "Vdc": 300.0,
            "f_output": 50.0,
            "f_carrier": 5000.0,
            "modulation_index": 0.85,
            "R_load": 20.0,
            "L_load": 0.01,
            "C_load": 0.0,
            "control_mode": "SPWM",
        }
    )
    result = converter.simulate(0.08, 4000)
    print("SPWM inverter metrics:")
    for k, v in result.metrics.items():
        print(f"{k}: {v:.4f}")


if __name__ == "__main__":
    main()
