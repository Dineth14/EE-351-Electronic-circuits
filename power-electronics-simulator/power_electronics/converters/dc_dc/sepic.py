"""SEPIC converter model."""

from __future__ import annotations

import numpy as np

from power_electronics.converters.dc_dc.boost import BoostConverter
from power_electronics.core.base_converter import ConverterInfo, SimulationResult


class SepicConverter(BoostConverter):
    """Simplified SEPIC model with dual-inductor waveform outputs."""

    converter_name = "sepic"

    def simulate(self, t_end: float, num_points: int) -> SimulationResult:
        result = super().simulate(t_end, num_points)
        il = result.signals["IL"]
        result.signals["IL1"] = il
        result.signals["IL2"] = 0.9 * il
        result.signals["VC"] = float(self.params["Vin"]) * np.ones_like(result.time)
        result.signals["Q_gate"] = result.signals["switch_Q"]
        return result

    def get_theoretical_values(self) -> dict[str, float]:
        vin = float(self.params["Vin"])
        d = float(self.params["duty_cycle"])
        return {"Vout_avg": vin * d / max(1.0 - d, 1e-6)}

    @staticmethod
    def get_info() -> ConverterInfo:
        return ConverterInfo(
            name="SEPIC Converter",
            category="DC-DC",
            description="Non-inverting buck-boost topology with series energy transfer capacitor.",
            equations=[r"V_o=\frac{D}{1-D}V_{in}"],
        )
