"""Buck-boost converter model."""

from __future__ import annotations

import numpy as np

from power_electronics.converters.dc_dc._common import DCDCBaseConverter
from power_electronics.core.base_converter import ConverterInfo, SimulationResult


class BuckBoostConverter(DCDCBaseConverter):
    """Inverting buck-boost converter with continuous state simulation."""

    converter_name = "buck_boost"

    def simulate(self, t_end: float, num_points: int) -> SimulationResult:
        p = self.params
        vin = float(p["Vin"])
        l_val = float(p["L"])
        c_val = float(p["C"])
        r_load = float(p["R_load"])
        r_l = float(p["R_L"])

        def on_state(il: float, vout: float) -> tuple[float, float]:
            return ((vin - il * r_l) / l_val, (-vout / r_load) / c_val)

        def off_state(il: float, vout: float) -> tuple[float, float]:
            return ((-vout - il * r_l) / l_val, (-il - vout / r_load) / c_val)

        t, signals, metrics = self._simulate_two_state(t_end, num_points, on_state, off_state)
        signals["Vout"] = -np.abs(signals["Vout"])
        signals["Iout"] = signals["Vout"] / max(float(self.params["R_load"]), 1e-6)
        metrics["Vout_avg"] = float(np.mean(signals["Vout"]))
        return self._result(t, signals, metrics)

    def get_theoretical_values(self) -> dict[str, float]:
        vin = float(self.params["Vin"])
        d = float(self.params["duty_cycle"])
        return {"Vout_avg": -vin * d / max(1.0 - d, 1e-6)}

    @staticmethod
    def get_param_schema() -> dict[str, dict[str, float | str]]:
        return BuckBoostConverter._base_schema()

    @staticmethod
    def get_info() -> ConverterInfo:
        return ConverterInfo(
            name="Buck-Boost Converter",
            category="DC-DC",
            description="Inverting converter capable of stepping voltage up or down.",
            equations=[r"V_o=-\frac{D}{1-D}V_{in}"],
        )
