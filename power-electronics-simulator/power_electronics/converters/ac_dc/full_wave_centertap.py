"""Single-phase center-tap full-wave rectifier."""

from __future__ import annotations

import numpy as np

from power_electronics.converters.ac_dc.half_wave import _rc_filter
from power_electronics.core.base_converter import BaseConverter, ConverterInfo, SimulationResult


class FullWaveCenterTapRectifier(BaseConverter):
    """Center-tap full-wave rectifier model."""

    def simulate(self, t_end: float, num_points: int) -> SimulationResult:
        p = self.params
        vm = float(p["Vac_peak"])
        f = float(p["frequency"])
        r = float(p["R_load"])
        c_filter = float(p.get("C_filter", 0.0))

        t = np.linspace(0.0, t_end, num_points)
        dt = t[1] - t[0]
        vac = vm * np.sin(2.0 * np.pi * f * t)
        v_raw = np.abs(vac)
        v_f = _rc_filter(v_raw, dt, r, c_filter) if c_filter > 0 else v_raw
        i_load = v_f / max(r, 1e-6)
        d1 = (vac >= 0).astype(float)
        d2 = 1.0 - d1
        il = np.gradient(v_f, dt) * float(p.get("L_filter", 0.0))
        ic = np.gradient(v_f, dt) * c_filter

        metrics = {
            "Vdc_avg": float(np.mean(v_f)),
            "Vdc_rms": float(np.sqrt(np.mean(v_f**2))),
            "Vripple_%": self.compute_ripple(v_f),
            "PIV": float(2.0 * vm),
            "THD_%": self.compute_THD(v_f, f, 1.0 / dt),
            "power_factor": float(np.mean(vac * i_load) / (np.sqrt(np.mean(vac**2)) * np.sqrt(np.mean(i_load**2)) + 1e-12)),
            "efficiency_%": self.compute_efficiency(float(np.mean(np.abs(vac * i_load))), float(np.mean(v_f * i_load))),
        }
        signals = {
            "Vac": vac,
            "Vdc_raw": v_raw,
            "Vdc_filtered": v_f,
            "Iload": i_load,
            "diode_states": d1 + 2.0 * d2,
            "Iripple": i_load - np.mean(i_load),
            "Vripple": v_f - np.mean(v_f),
        }
        return SimulationResult(t, signals, metrics, "full_wave_centertap", dict(self.params))

    def get_theoretical_values(self) -> dict[str, float]:
        vm = float(self.params["Vac_peak"])
        return {"Vdc_avg": 2.0 * vm / np.pi}

    @staticmethod
    def get_param_schema() -> dict[str, dict[str, float | str]]:
        return {
            **{
                "Vac_peak": {"type": "float", "min": 50.0, "max": 400.0, "step": 1.0, "default": 170.0, "unit": "V", "label": "AC Peak Voltage"},
                "frequency": {"type": "float", "min": 40.0, "max": 500.0, "step": 1.0, "default": 50.0, "unit": "Hz", "label": "Input Frequency"},
                "R_load": {"type": "float", "min": 1.0, "max": 200.0, "step": 1.0, "default": 20.0, "unit": "ohm", "label": "Load Resistance"},
                "L_filter": {"type": "float", "min": 0.0, "max": 0.2, "step": 0.001, "default": 0.001, "unit": "H", "label": "Filter Inductance"},
                "C_filter": {"type": "float", "min": 0.0, "max": 0.02, "step": 0.0001, "default": 0.002, "unit": "F", "label": "Filter Capacitance"},
            }
        }

    @staticmethod
    def get_info() -> ConverterInfo:
        return ConverterInfo(
            name="1-Phase Full-Wave Center-Tap Rectifier",
            category="AC-DC",
            description="Two diodes with center-tapped transformer enable full-wave rectification.",
            equations=[r"V_{dc,avg}=\frac{2V_m}{\pi}", r"\text{PIV}=2V_m"],
        )
