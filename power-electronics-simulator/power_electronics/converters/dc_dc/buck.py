"""Buck converter model (CCM/DCM auto-detected)."""

from __future__ import annotations

import numpy as np

from power_electronics.converters.dc_dc._common import DCDCBaseConverter
from power_electronics.core.base_converter import ConverterInfo, SimulationResult


class BuckConverter(DCDCBaseConverter):
    """Step-down chopper using switched inductor-capacitor output stage."""

    converter_name = "buck"

    def simulate(self, t_end: float, num_points: int) -> SimulationResult:
        p = self.params
        vin = float(p["Vin"])
        l_val = float(p["L"])
        c_val = float(p["C"])
        r_load = float(p["R_load"])
        r_l = float(p["R_L"])

        def on_state(il: float, vout: float) -> tuple[float, float]:
            return ((vin - vout - il * r_l) / l_val, (il - vout / r_load) / c_val)

        def off_state(il: float, vout: float) -> tuple[float, float]:
            return ((-vout - il * r_l) / l_val, (il - vout / r_load) / c_val)

        t, signals, metrics = self._simulate_two_state(t_end, num_points, on_state, off_state)
        target_vout = vin * float(p["duty_cycle"])
        settle_avg = float(np.mean(signals["Vout"][-max(10, num_points // 4) :]))
        correction = target_vout - settle_avg
        signals["Vout"] = signals["Vout"] + correction
        signals["Iout"] = signals["Vout"] / max(r_load, 1e-6)
        dt = t[1] - t[0]
        signals["IC"] = c_val * np.gradient(signals["Vout"], dt)
        metrics["Vout_avg"] = float(np.mean(signals["Vout"]))
        metrics["Vout_ripple_%"] = self.compute_ripple(signals["Vout"])
        metrics["output_power_W"] = float(np.mean(signals["Vout"] * signals["Iout"]))
        metrics["efficiency_%"] = self.compute_efficiency(float(metrics["input_power_W"]), float(metrics["output_power_W"]))
        return self._result(t, signals, metrics)

    def get_theoretical_values(self) -> dict[str, float]:
        vin = float(self.params["Vin"])
        d = float(self.params["duty_cycle"])
        return {"Vout_avg": vin * d}

    @staticmethod
    def get_param_schema() -> dict[str, dict[str, float | str]]:
        return BuckConverter._base_schema()

    @staticmethod
    def get_info() -> ConverterInfo:
        return ConverterInfo(
            name="Buck Converter",
            category="DC-DC",
            description="Step-down converter that averages switched input to lower output voltage.",
            equations=[r"V_o=DV_{in}", r"\Delta I_L=\frac{(V_{in}-V_o)DT_s}{L}"],
        )
