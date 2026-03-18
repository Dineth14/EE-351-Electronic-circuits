"""SCR controlled half-wave rectifier."""

from __future__ import annotations

import numpy as np

from power_electronics.converters.ac_dc.half_wave import HalfWaveRectifier, _rc_filter
from power_electronics.core.base_converter import ConverterInfo, SimulationResult


class SCRHalfWaveRectifier(HalfWaveRectifier):
    """Half-wave controlled rectifier using firing-angle control."""

    def simulate(self, t_end: float, num_points: int) -> SimulationResult:
        p = self.params
        vm = float(p["Vac_peak"])
        f = float(p["frequency"])
        r = float(p["R_load"])
        c = float(p.get("C_filter", 0.0))
        alpha_deg = float(p.get("alpha_deg", 45.0))
        alpha = np.deg2rad(np.clip(alpha_deg, 0.0, 180.0))
        t = np.linspace(0.0, t_end, num_points)
        dt = t[1] - t[0]

        omega = 2.0 * np.pi * f
        theta = np.mod(omega * t, 2.0 * np.pi)
        vac = vm * np.sin(theta)
        conducting = (theta >= alpha) & (theta <= np.pi)
        v_raw = np.where(conducting, vac, 0.0)
        v_f = _rc_filter(v_raw, dt, r, c) if c > 0 else v_raw
        i_load = v_f / max(r, 1e-6)
        pulses = ((theta >= alpha) & (theta < alpha + 0.08)).astype(float)

        signals = {
            "Vac": vac,
            "Vdc_raw": v_raw,
            "Vdc_filtered": v_f,
            "Iload": i_load,
            "diode_states": conducting.astype(float),
            "Iripple": i_load - np.mean(i_load),
            "Vripple": v_f - np.mean(v_f),
            "Vout": v_f,
            "ID_SCR": conducting.astype(float) * i_load,
            "firing_pulse": pulses,
            "alpha_marker": np.full_like(t, alpha_deg),
        }
        pin = float(np.mean(np.abs(vac * i_load)))
        pout = float(np.mean(v_f * i_load))
        metrics = {
            "Vdc_avg": float(np.mean(v_f)),
            "Vdc_rms": float(np.sqrt(np.mean(v_f**2))),
            "Vripple_%": self.compute_ripple(v_f),
            "PIV": float(vm),
            "THD_%": self.compute_THD(v_f, f, 1.0 / dt),
            "power_factor": float(np.mean(vac * i_load) / (np.sqrt(np.mean(vac**2)) * np.sqrt(np.mean(i_load**2)) + 1e-12)),
            "efficiency_%": self.compute_efficiency(pin, pout),
        }
        return SimulationResult(t, signals, metrics, "scr_half_wave", dict(self.params))

    def get_theoretical_values(self) -> dict[str, float]:
        vm = float(self.params["Vac_peak"])
        alpha = np.deg2rad(float(self.params.get("alpha_deg", 45.0)))
        return {"Vdc_avg": vm * (1.0 + np.cos(alpha)) / (2.0 * np.pi)}

    @staticmethod
    def get_param_schema() -> dict[str, dict[str, float | str]]:
        schema = HalfWaveRectifier.get_param_schema()
        schema["alpha_deg"] = {"type": "float", "min": 0.0, "max": 170.0, "step": 1.0, "default": 45.0, "unit": "deg", "label": "Firing Angle"}
        return schema

    @staticmethod
    def get_info() -> ConverterInfo:
        return ConverterInfo(
            name="SCR Half-Wave Controlled Rectifier",
            category="AC-DC",
            description="Firing-angle control varies average DC output from half-wave conversion.",
            equations=[r"V_{dc,avg}=\frac{V_m}{2\pi}(1+\cos\alpha)"],
        )
