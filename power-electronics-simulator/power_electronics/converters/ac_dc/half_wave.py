"""Single-phase half-wave uncontrolled rectifier."""

from __future__ import annotations

import numpy as np

from power_electronics.core.base_converter import BaseConverter, ConverterInfo, SimulationResult


def _rc_filter(v_raw: np.ndarray, dt: float, r_load: float, c_filter: float) -> np.ndarray:
    tau = max(r_load * c_filter, 1e-9)
    alpha = dt / (tau + dt)
    out = np.zeros_like(v_raw)
    for i in range(1, v_raw.size):
        out[i] = out[i - 1] + alpha * (v_raw[i] - out[i - 1])
    return out


class HalfWaveRectifier(BaseConverter):
    """Half-wave diode rectifier with optional RC output filtering."""

    def simulate(self, t_end: float, num_points: int) -> SimulationResult:
        p = self.params
        vac_peak = float(p["Vac_peak"])
        f = float(p["frequency"])
        r_load = float(p["R_load"])
        c_filter = float(p.get("C_filter", 0.0))

        t = np.linspace(0.0, t_end, num_points)
        dt = t[1] - t[0]
        vac = vac_peak * np.sin(2.0 * np.pi * f * t)
        v_raw = np.maximum(vac, 0.0)
        v_filt = _rc_filter(v_raw, dt, r_load, c_filter) if c_filter > 0 else v_raw.copy()
        i_load = v_filt / max(r_load, 1e-6)
        idiode = (vac > 0).astype(float) * i_load
        il = np.gradient(v_filt, dt) * float(p.get("L_filter", 0.0))
        ic = np.gradient(v_filt, dt) * c_filter
        vripple = v_filt - np.mean(v_filt)
        iripple = i_load - np.mean(i_load)

        signals = {
            "Vac": vac,
            "Vdc_raw": v_raw,
            "Vdc_filtered": v_filt,
            "Iload": i_load,
            "diode_states": (vac > 0).astype(float),
            "Iripple": iripple,
            "Vripple": vripple,
            "Vout_raw": v_raw,
            "Vout_filtered": v_filt,
            "ID": idiode,
            "IL": il,
            "IC": ic,
        }
        pin = float(np.mean(np.abs(vac * idiode)))
        pout = float(np.mean(v_filt * i_load))
        metrics = {
            "Vdc_avg": float(np.mean(v_filt)),
            "Vdc_rms": float(np.sqrt(np.mean(v_filt**2))),
            "Vripple_%": self.compute_ripple(v_filt),
            "PIV": float(vac_peak),
            "THD_%": self.compute_THD(v_filt, f, 1.0 / dt),
            "power_factor": float(np.mean(vac * idiode) / (np.sqrt(np.mean(vac**2)) * np.sqrt(np.mean(idiode**2)) + 1e-12)),
            "efficiency_%": self.compute_efficiency(pin, pout),
        }
        return SimulationResult(t, signals, metrics, "half_wave", dict(self.params))

    def get_theoretical_values(self) -> dict[str, float]:
        vm = float(self.params["Vac_peak"])
        r = float(self.params["R_load"])
        return {"Vdc_avg": vm / np.pi, "Idc_avg": vm / (np.pi * r)}

    @staticmethod
    def get_param_schema() -> dict[str, dict[str, float | str]]:
        return {
            "Vac_peak": {"type": "float", "min": 50.0, "max": 400.0, "step": 1.0, "default": 170.0, "unit": "V", "label": "AC Peak Voltage"},
            "frequency": {"type": "float", "min": 40.0, "max": 500.0, "step": 1.0, "default": 50.0, "unit": "Hz", "label": "Input Frequency"},
            "R_load": {"type": "float", "min": 1.0, "max": 200.0, "step": 1.0, "default": 20.0, "unit": "ohm", "label": "Load Resistance"},
            "L_filter": {"type": "float", "min": 0.0, "max": 0.2, "step": 0.001, "default": 0.001, "unit": "H", "label": "Filter Inductance"},
            "C_filter": {"type": "float", "min": 0.0, "max": 0.02, "step": 0.0001, "default": 0.002, "unit": "F", "label": "Filter Capacitance"},
        }

    @staticmethod
    def get_info() -> ConverterInfo:
        return ConverterInfo(
            name="1-Phase Half-Wave Rectifier",
            category="AC-DC",
            description="Single diode rectifier conducting during positive half cycles.",
            equations=[r"V_{dc,avg}=\frac{V_m}{\pi}", r"\text{PIV}=V_m"],
        )
