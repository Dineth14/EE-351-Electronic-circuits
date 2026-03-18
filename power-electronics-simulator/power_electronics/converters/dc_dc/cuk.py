"""Cuk converter model."""

from __future__ import annotations

import numpy as np

from power_electronics.converters.dc_dc.buck_boost import BuckBoostConverter
from power_electronics.core.base_converter import ConverterInfo, SimulationResult


class CukConverter(BuckBoostConverter):
    """Simplified Cuk converter based on buck-boost transfer with dual inductor signals."""

    converter_name = "cuk"

    def simulate(self, t_end: float, num_points: int) -> SimulationResult:
        result = super().simulate(t_end, num_points)
        il = result.signals["IL"]
        vout = result.signals["Vout"]
        vc1 = float(self.params["Vin"]) - vout
        result.signals["IL1"] = il
        result.signals["IL2"] = 0.8 * il
        result.signals["VC1"] = vc1
        result.signals["Q_gate"] = result.signals["switch_Q"]
        return result

    @staticmethod
    def get_info() -> ConverterInfo:
        return ConverterInfo(
            name="Cuk Converter",
            category="DC-DC",
            description="Inverting converter with continuous input and output currents.",
            equations=[r"V_o=-\frac{D}{1-D}V_{in}", r"C_1\text{ transfers energy}"],
        )
