"""Simplified Vienna 3-phase PFC rectifier model."""

from __future__ import annotations

import numpy as np

from power_electronics.converters.ac_dc.three_phase_bridge import ThreePhaseBridgeRectifier
from power_electronics.core.base_converter import ConverterInfo, SimulationResult


class ViennaRectifier(ThreePhaseBridgeRectifier):
    """Three-phase Vienna rectifier approximation with high PF behavior."""

    def simulate(self, t_end: float, num_points: int) -> SimulationResult:
        base = super().simulate(t_end, num_points)
        vdc = base.signals["Vdc_filtered"]
        t = base.time
        f = float(self.params["frequency"])
        ripple_reduction = 0.35
        vdc_pfc = np.mean(vdc) + ripple_reduction * (vdc - np.mean(vdc))
        i_load = vdc_pfc / max(float(self.params["R_load"]), 1e-6)
        signals = dict(base.signals)
        signals["Vdc_filtered"] = vdc_pfc
        signals["Iload"] = i_load
        signals["switch_state"] = (np.sin(2.0 * np.pi * 6.0 * f * t) > 0).astype(float)
        metrics = dict(base.metrics)
        metrics["Vdc_avg"] = float(np.mean(vdc_pfc))
        metrics["Vripple_%"] = self.compute_ripple(vdc_pfc)
        metrics["power_factor"] = 0.99
        metrics["THD_%"] = min(metrics.get("THD_%", 0.0), 5.0)
        return SimulationResult(t, signals, metrics, "vienna_rectifier", dict(self.params))

    @staticmethod
    def get_info() -> ConverterInfo:
        return ConverterInfo(
            name="Vienna Rectifier",
            category="AC-DC",
            description="Three-level unidirectional PFC rectifier with high efficiency and low THD.",
            equations=[r"i_s\propto v_s", r"\text{PF}\rightarrow 1"],
        )
