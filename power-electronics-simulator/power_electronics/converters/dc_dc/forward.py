"""Forward converter model."""

from __future__ import annotations

import numpy as np

from power_electronics.converters.dc_dc.buck import BuckConverter
from power_electronics.core.base_converter import ConverterInfo, SimulationResult


class ForwardConverter(BuckConverter):
    """Simplified isolated forward converter with turns ratio n."""

    converter_name = "forward"

    def simulate(self, t_end: float, num_points: int) -> SimulationResult:
        n = float(self.params.get("n", 1.5))
        original_vin = float(self.params["Vin"])
        self.params["Vin"] = original_vin * n
        result = super().simulate(t_end, num_points)
        self.params["Vin"] = original_vin
        result.signals["Vin"] = np.full_like(result.time, original_vin)
        result.signals["Q_gate"] = result.signals["switch_Q"]
        result.converter_name = "forward"
        return result

    def get_theoretical_values(self) -> dict[str, float]:
        vin = float(self.params["Vin"])
        d = float(self.params["duty_cycle"])
        n = float(self.params.get("n", 1.5))
        return {"Vout_avg": vin * n * d}

    @staticmethod
    def get_param_schema() -> dict[str, dict[str, float | str]]:
        schema = ForwardConverter._base_schema()
        schema["n"] = {"type": "float", "min": 0.2, "max": 5.0, "step": 0.1, "default": 1.5, "unit": "", "label": "Turns Ratio n"}
        return schema

    @staticmethod
    def get_info() -> ConverterInfo:
        return ConverterInfo(
            name="Forward Converter",
            category="DC-DC",
            description="Transformer-coupled buck-like topology with direct energy transfer during ON interval.",
            equations=[r"V_o=nDV_{in}"],
        )
