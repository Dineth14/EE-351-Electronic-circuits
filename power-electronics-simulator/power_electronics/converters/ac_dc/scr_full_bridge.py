"""SCR controlled single-phase full-bridge rectifier."""

from __future__ import annotations

import numpy as np

from power_electronics.converters.ac_dc.full_bridge import FullBridgeRectifier
from power_electronics.converters.ac_dc.half_wave import _rc_filter
from power_electronics.core.base_converter import ConverterInfo, SimulationResult


class SCRFullBridgeRectifier(FullBridgeRectifier):
    """Single-phase fully controlled bridge rectifier model."""

    def simulate(self, t_end: float, num_points: int) -> SimulationResult:
        p = self.params
        vm = float(p["Vac_peak"])
        f = float(p["frequency"])
        r = float(p["R_load"])
        c = float(p.get("C_filter", 0.0))
        alpha_deg = float(p.get("alpha_deg", 30.0))
        alpha = np.deg2rad(np.clip(alpha_deg, 0.0, 170.0))

        t = np.linspace(0.0, t_end, num_points)
        dt = t[1] - t[0]
        omega = 2.0 * np.pi * f
        theta = np.mod(omega * t, 2.0 * np.pi)
        vac = vm * np.sin(theta)

        cond_pos = (theta >= alpha) & (theta <= np.pi)
        cond_neg = (theta >= np.pi + alpha) & (theta <= 2.0 * np.pi)
        v_raw = np.where(cond_pos, vac, 0.0) - np.where(cond_neg, vac, 0.0)
        v_raw = np.abs(v_raw)
        v_f = _rc_filter(v_raw, dt, r, c) if c > 0 else v_raw
        i_load = v_f / max(r, 1e-6)

        p1 = ((theta >= alpha) & (theta < alpha + 0.08)).astype(float)
        p2 = ((theta >= np.pi + alpha) & (theta < np.pi + alpha + 0.08)).astype(float)
        pulses = p1 + p2

        signals = {
            "Vac": vac,
            "Vdc_raw": v_raw,
            "Vdc_filtered": v_f,
            "Iload": i_load,
            "diode_states": np.vstack([cond_pos, cond_pos, cond_neg, cond_neg]).T.astype(float),
            "Iripple": i_load - np.mean(i_load),
            "Vripple": v_f - np.mean(v_f),
            "Vout": v_f,
            "ID1": cond_pos.astype(float) * i_load,
            "ID2": cond_pos.astype(float) * i_load,
            "ID3": cond_neg.astype(float) * i_load,
            "ID4": cond_neg.astype(float) * i_load,
            "firing_pulses": pulses,
            "alpha_marker": np.full_like(t, alpha_deg),
        }
        pin = float(np.mean(np.abs(vac * i_load)))
        pout = float(np.mean(v_f * i_load))
        metrics = {
            "Vdc_avg": float(np.mean(v_f)),
            "Vdc_rms": float(np.sqrt(np.mean(v_f**2))),
            "Vripple_%": self.compute_ripple(v_f),
            "PIV": float(vm),
            "THD_%": self.compute_THD(v_f, 2.0 * f, 1.0 / dt),
            "power_factor": float(np.mean(vac * i_load) / (np.sqrt(np.mean(vac**2)) * np.sqrt(np.mean(i_load**2)) + 1e-12)),
            "efficiency_%": self.compute_efficiency(pin, pout),
        }
        return SimulationResult(t, signals, metrics, "scr_full_bridge", dict(self.params))

    def get_theoretical_values(self) -> dict[str, float]:
        vm = float(self.params["Vac_peak"])
        alpha = np.deg2rad(float(self.params.get("alpha_deg", 30.0)))
        return {"Vdc_avg": 2.0 * vm * np.cos(alpha) / np.pi}

    @staticmethod
    def get_param_schema() -> dict[str, dict[str, float | str]]:
        schema = FullBridgeRectifier.get_param_schema()
        schema["alpha_deg"] = {"type": "float", "min": 0.0, "max": 170.0, "step": 1.0, "default": 30.0, "unit": "deg", "label": "Firing Angle"}
        return schema

    @staticmethod
    def get_info() -> ConverterInfo:
        return ConverterInfo(
            name="SCR Full-Bridge Controlled Rectifier",
            category="AC-DC",
            description="Fully controlled bridge with variable delay angle alpha.",
            equations=[r"V_{dc,avg}=\frac{2V_m}{\pi}\cos\alpha"],
        )
