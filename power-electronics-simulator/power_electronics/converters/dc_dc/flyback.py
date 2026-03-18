"""Flyback converter model."""

from __future__ import annotations

import numpy as np

from power_electronics.converters.dc_dc._common import DCDCBaseConverter
from power_electronics.core.base_converter import ConverterInfo, SimulationResult


class FlybackConverter(DCDCBaseConverter):
    """Isolated flyback converter with transformer turns ratio n."""

    converter_name = "flyback"

    def simulate(self, t_end: float, num_points: int) -> SimulationResult:
        p = self.params
        n = float(p.get("n", 2.0))
        vin = float(p["Vin"])
        l_val = float(p["L"])
        c_val = float(p["C"])
        r_load = float(p["R_load"])
        r_l = float(p["R_L"])

        def on_state(il: float, vout: float) -> tuple[float, float]:
            return ((vin - il * r_l) / l_val, (-vout / r_load) / c_val)

        def off_state(il: float, vout: float) -> tuple[float, float]:
            isec = il * n
            return ((-vout / max(n, 1e-6) - il * r_l) / l_val, (isec - vout / r_load) / c_val)

        t, signals, metrics = self._simulate_two_state(t_end, num_points, on_state, off_state)
        q = signals["switch_Q"]
        ip = signals["IL"]
        isec = np.where(q < 0.5, ip * n, 0.0)
        signals["IP"] = ip
        signals["IS"] = isec
        signals["Vmag"] = vin * q
        signals["Q_gate"] = q
        metrics["Vout_avg"] = float(np.mean(signals["Vout"]))
        return self._result(t, signals, metrics)

    def get_theoretical_values(self) -> dict[str, float]:
        vin = float(self.params["Vin"])
        d = float(self.params["duty_cycle"])
        n = float(self.params.get("n", 2.0))
        return {"Vout_avg": vin * n * d / max(1.0 - d, 1e-6)}

    @staticmethod
    def get_param_schema() -> dict[str, dict[str, float | str]]:
        schema = FlybackConverter._base_schema()
        schema["n"] = {"type": "float", "min": 0.2, "max": 10.0, "step": 0.1, "default": 2.0, "unit": "", "label": "Turns Ratio n"}
        return schema

    @staticmethod
    def get_info() -> ConverterInfo:
        return ConverterInfo(
            name="Flyback Converter",
            category="DC-DC",
            description="Isolated energy-storage converter using transformer magnetizing inductance.",
            equations=[r"V_o=\frac{nD}{1-D}V_{in}"],
        )
