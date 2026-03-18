"""Three-phase half-wave rectifier (M3)."""

from __future__ import annotations

import numpy as np

from power_electronics.converters.ac_dc.half_wave import _rc_filter
from power_electronics.core.base_converter import BaseConverter, ConverterInfo, SimulationResult


class ThreePhaseHalfRectifier(BaseConverter):
    """Three-phase half-wave rectifier selecting maximum phase voltage."""

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
        v_raw = np.maximum.reduce([va, vb, vc])
        v_raw = np.maximum(v_raw, 0.0)
        vdc = _rc_filter(v_raw, dt, r, c) if c > 0 else v_raw
        iload = vdc / max(r, 1e-6)
        idx = np.argmax(np.vstack([va, vb, vc]), axis=0)
        diode_states = np.eye(3)[idx]

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
            "IL": iload,
        }
        vac_line = np.sqrt((va**2 + vb**2 + vc**2) / 3.0)
        pin = float(np.mean(vac_line * iload))
        pout = float(np.mean(vdc * iload))
        metrics = {
            "Vdc_avg": float(np.mean(vdc)),
            "Vdc_rms": float(np.sqrt(np.mean(vdc**2))),
            "Vripple_%": self.compute_ripple(vdc),
            "PIV": float(np.sqrt(3) * vm),
            "THD_%": self.compute_THD(vdc, 3.0 * f, 1.0 / dt),
            "power_factor": float(np.mean(vdc * iload) / (np.sqrt(np.mean(vdc**2)) * np.sqrt(np.mean(iload**2)) + 1e-12)),
            "efficiency_%": self.compute_efficiency(pin, pout),
        }
        return SimulationResult(t, signals, metrics, "three_phase_half", dict(self.params))

    def get_theoretical_values(self) -> dict[str, float]:
        vm = float(self.params["Vac_peak"])
        return {"Vdc_avg": 1.17 * vm}

    @staticmethod
    def get_param_schema() -> dict[str, dict[str, float | str]]:
        return {
            "Vac_peak": {"type": "float", "min": 50.0, "max": 450.0, "step": 1.0, "default": 170.0, "unit": "V", "label": "Phase Peak Voltage"},
            "frequency": {"type": "float", "min": 40.0, "max": 400.0, "step": 1.0, "default": 50.0, "unit": "Hz", "label": "Grid Frequency"},
            "R_load": {"type": "float", "min": 1.0, "max": 300.0, "step": 1.0, "default": 30.0, "unit": "ohm", "label": "Load Resistance"},
            "L_filter": {"type": "float", "min": 0.0, "max": 0.2, "step": 0.001, "default": 0.005, "unit": "H", "label": "Filter Inductance"},
            "C_filter": {"type": "float", "min": 0.0, "max": 0.05, "step": 0.0001, "default": 0.003, "unit": "F", "label": "Filter Capacitance"},
        }

    @staticmethod
    def get_info() -> ConverterInfo:
        return ConverterInfo(
            name="Three-Phase Half-Wave Rectifier",
            category="AC-DC",
            description="M3 rectifier with one conducting diode at any instant.",
            equations=[r"V_{dc,avg}\approx1.17V_{phase,peak}"] ,
        )
