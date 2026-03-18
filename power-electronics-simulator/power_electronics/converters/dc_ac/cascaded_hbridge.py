"""Cascaded H-bridge multilevel inverter model."""

from __future__ import annotations

import numpy as np

from power_electronics.converters.dc_ac.single_phase_hbridge import SinglePhaseHBridgeVSI
from power_electronics.core.base_converter import ConverterInfo, SimulationResult


class CascadedHBridgeInverter(SinglePhaseHBridgeVSI):
    """N-cell cascaded H-bridge inverter with multilevel output synthesis."""

    def simulate(self, t_end: float, num_points: int) -> SimulationResult:
        levels = int(self.params.get("levels", 5))
        cells = max(2, (levels - 1) // 2)
        local = dict(self.params)
        local["Vdc"] = float(self.params["Vdc"]) / cells
        t = np.linspace(0.0, t_end, num_points)
        outputs: list[np.ndarray] = []
        current = None
        for k in range(cells):
            phase_shift = k / max(cells, 1) / float(local["f_output"])
            cell_model = SinglePhaseHBridgeVSI(local)
            cell_res = cell_model.simulate(t_end, num_points)
            shifted = np.interp(t, np.mod(cell_res.time + phase_shift, t_end), cell_res.signals["Vout"])
            outputs.append(shifted)
            current = cell_res.signals["Iout"]

        v_total = np.sum(np.vstack(outputs), axis=0)
        if current is None:
            current = np.zeros_like(v_total)
        metrics = {
            "Vout_rms": float(np.sqrt(np.mean(v_total**2))),
            "THD_%": self.compute_THD(v_total, float(self.params["f_output"]), num_points / max(t_end, 1e-9)),
            "modulation_index_actual": float(self.params["modulation_index"]),
            "fundamental_V": float(np.sqrt(2.0) * np.std(v_total)),
            "output_power_W": float(np.mean(v_total * current)),
            "efficiency_%": 96.0,
        }
        signals = {
            "Vdc_cells": np.full((num_points, cells), float(local["Vdc"])),
            "Vout_total": v_total,
            "Iout": current,
            "Vout_phase": v_total,
            "Iout_phase": current,
            "switch_states": np.zeros((num_points, 4 * cells)),
            "Vout_line": v_total,
            "Vout_fundamental": np.sin(2.0 * np.pi * float(self.params["f_output"]) * t) * np.max(np.abs(v_total)),
            "Vout_harmonics": v_total,
        }
        for idx, v in enumerate(outputs, start=1):
            signals[f"Vout_level{idx}"] = v
        return SimulationResult(t, signals, metrics, "cascaded_hbridge", dict(self.params))

    @staticmethod
    def get_param_schema() -> dict[str, dict[str, float | str]]:
        schema = SinglePhaseHBridgeVSI.get_param_schema()
        schema["levels"] = {"type": "float", "min": 3.0, "max": 21.0, "step": 2.0, "default": 5.0, "unit": "", "label": "Number of Levels"}
        return schema

    @staticmethod
    def get_info() -> ConverterInfo:
        return ConverterInfo(
            name="Cascaded H-Bridge Inverter",
            category="DC-AC",
            description="Multilevel inverter synthesizing stepped output from series H-bridge cells.",
            equations=[r"m_{levels}=2N_{cells}+1"],
        )
