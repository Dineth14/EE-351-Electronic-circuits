"""Three-phase full-bridge rectifier (B6)."""

from __future__ import annotations

import numpy as np

from power_electronics.converters.ac_dc.half_wave import _rc_filter
from power_electronics.core.base_converter import BaseConverter, ConverterInfo, SimulationResult


class ThreePhaseBridgeRectifier(BaseConverter):
    """B6 diode bridge rectifier selecting highest and lowest phase pair."""

    def simulate(self, t_end: float, num_points: int) -> SimulationResult:
        p = self.params
        vm = float(p["Vac_peak"])
        f = float(p["frequency"])
        r = float(p["R_load"])
        c = float(p.get("C_filter", 0.0))
        t = np.linspace(0.0, t_end, num_points)
        dt = t[1] - t[0]

        va = vm * np.sin(2.0 * np.pi * f * t)
        vb = vm * np.sin(2.0 * np.pi * f * t - 2.0 * np.pi / 3.0)
        vc = vm * np.sin(2.0 * np.pi * f * t + 2.0 * np.pi / 3.0)
        stacked = np.vstack([va, vb, vc])
        vmax = np.max(stacked, axis=0)
        vmin = np.min(stacked, axis=0)
        v_raw = vmax - vmin
        vdc = _rc_filter(v_raw, dt, r, c) if c > 0 else v_raw
        iload = vdc / max(r, 1e-6)
        idx_max = np.argmax(stacked, axis=0)
        idx_min = np.argmin(stacked, axis=0)
        diode_states = np.zeros((num_points, 6), dtype=float)
        for i in range(num_points):
            diode_states[i, idx_max[i]] = 1.0
            diode_states[i, idx_min[i] + 3] = 1.0

        signals = {
            "Vac": va,
            "Vdc_raw": v_raw,
            "Vdc_filtered": vdc,
            "Iload": iload,
            "diode_states": diode_states,
            "Iripple": iload - np.mean(iload),
            "Vripple": vdc - np.mean(vdc),
            "Va": va,
            "Vb": vb,
            "Vc": vc,
            "Vout": vdc,
            "ID1": diode_states[:, 0] * iload,
            "ID2": diode_states[:, 1] * iload,
            "ID3": diode_states[:, 2] * iload,
            "ID4": diode_states[:, 3] * iload,
            "ID5": diode_states[:, 4] * iload,
            "ID6": diode_states[:, 5] * iload,
            "IL": iload,
        }
        pin = float(np.mean(v_raw * iload))
        pout = float(np.mean(vdc * iload))
        metrics = {
            "Vdc_avg": float(np.mean(vdc)),
            "Vdc_rms": float(np.sqrt(np.mean(vdc**2))),
            "Vripple_%": self.compute_ripple(vdc),
            "PIV": float(vm),
            "THD_%": self.compute_THD(vdc, 6.0 * f, 1.0 / dt),
            "power_factor": 0.955,
            "efficiency_%": self.compute_efficiency(pin, pout),
        }
        return SimulationResult(t, signals, metrics, "three_phase_bridge", dict(self.params))

    def get_theoretical_values(self) -> dict[str, float]:
        vm = float(self.params["Vac_peak"])
        return {"Vdc_avg": 1.35 * np.sqrt(2.0 / 3.0) * vm}

    @staticmethod
    def get_param_schema() -> dict[str, dict[str, float | str]]:
        return {
            "Vac_peak": {"type": "float", "min": 50.0, "max": 500.0, "step": 1.0, "default": 170.0, "unit": "V", "label": "Phase Peak Voltage"},
            "frequency": {"type": "float", "min": 40.0, "max": 400.0, "step": 1.0, "default": 50.0, "unit": "Hz", "label": "Grid Frequency"},
            "R_load": {"type": "float", "min": 2.0, "max": 300.0, "step": 1.0, "default": 25.0, "unit": "ohm", "label": "Load Resistance"},
            "L_filter": {"type": "float", "min": 0.0, "max": 0.2, "step": 0.001, "default": 0.01, "unit": "H", "label": "Filter Inductance"},
            "C_filter": {"type": "float", "min": 0.0, "max": 0.05, "step": 0.0001, "default": 0.004, "unit": "F", "label": "Filter Capacitance"},
        }

    @staticmethod
    def get_info() -> ConverterInfo:
        return ConverterInfo(
            name="Three-Phase Full-Bridge Rectifier (B6)",
            category="AC-DC",
            description="Six-diode bridge with 6-pulse rectified DC output.",
            equations=[r"V_{dc,avg}=1.35V_{LL,rms}", r"f_{ripple}=6f_{line}"],
        )
