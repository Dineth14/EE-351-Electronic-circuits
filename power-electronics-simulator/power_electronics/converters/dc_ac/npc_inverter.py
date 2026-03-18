"""Three-level NPC inverter model."""

from __future__ import annotations

import numpy as np

from power_electronics.converters.dc_ac.single_phase_hbridge import SinglePhaseHBridgeVSI
from power_electronics.core.base_converter import ConverterInfo, SimulationResult


class NPCInverter(SinglePhaseHBridgeVSI):
    """Three-level neutral-point clamped inverter approximation."""

    def simulate(self, t_end: float, num_points: int) -> SimulationResult:
        base = super().simulate(t_end, num_points)
        vout = base.signals["Vout"]
        levels = np.where(vout > 0.1 * np.max(np.abs(vout)), 1.0, np.where(vout < -0.1 * np.max(np.abs(vout)), -1.0, 0.0))
        v3 = levels * float(self.params["Vdc"]) / 2.0
        base.signals["Vout"] = v3
        base.signals["Vout_phase"] = v3
        base.signals["neutral_clamping"] = (levels == 0).astype(float)
        base.metrics["Vout_rms"] = float(np.sqrt(np.mean(v3**2)))
        base.metrics["THD_%"] = self.compute_THD(v3, float(self.params["f_output"]), num_points / max(t_end, 1e-9))
        base.converter_name = "npc_inverter"
        return base

    @staticmethod
    def get_info() -> ConverterInfo:
        return ConverterInfo(
            name="3-Level NPC Inverter",
            category="DC-AC",
            description="Diode-clamped three-level inverter reducing dv/dt and harmonic distortion.",
            equations=[r"v_o\in\{-V_{dc}/2,0,+V_{dc}/2\}"],
        )
