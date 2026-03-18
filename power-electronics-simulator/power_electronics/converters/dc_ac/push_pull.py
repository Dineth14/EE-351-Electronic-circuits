"""Push-pull inverter model."""

from __future__ import annotations

from power_electronics.converters.dc_ac.single_phase_hbridge import SinglePhaseHBridgeVSI
from power_electronics.core.base_converter import ConverterInfo, SimulationResult


class PushPullInverter(SinglePhaseHBridgeVSI):
    """Push-pull inverter approximated through two-leg square operation."""

    def simulate(self, t_end: float, num_points: int) -> SimulationResult:
        local = dict(self.params)
        local["control_mode"] = "square"
        model = SinglePhaseHBridgeVSI(local)
        result = model.simulate(t_end, num_points)
        result.converter_name = "push_pull"
        result.signals["switch_states"] = result.signals["switch_states"][:, :2]
        return result

    @staticmethod
    def get_info() -> ConverterInfo:
        return ConverterInfo(
            name="Push-Pull Inverter",
            category="DC-AC",
            description="Center-tapped transformer inverter driven by complementary switches.",
            equations=[r"V_o\propto nV_{dc}"],
        )
