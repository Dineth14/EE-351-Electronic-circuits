"""Single-phase H-bridge inverter."""

from __future__ import annotations

import numpy as np

from power_electronics.core.base_converter import BaseConverter, ConverterInfo, SimulationResult
from power_electronics.core.signal_generator import spwm


class SinglePhaseHBridgeVSI(BaseConverter):
    """Single-phase full-bridge voltage source inverter."""

    def simulate(self, t_end: float, num_points: int) -> SimulationResult:
        p = self.params
        vdc = float(p["Vdc"])
        f_out = float(p["f_output"])
        f_carrier = float(p["f_carrier"])
        m = float(p["modulation_index"])
        r_load = float(p["R_load"])
        l_load = float(p.get("L_load", 0.0))
        control_mode = str(p.get("control_mode", "SPWM"))

        t = np.linspace(0.0, t_end, num_points)
        dt = t[1] - t[0]
        ref = m * np.sin(2.0 * np.pi * f_out * t)
        carrier = 2.0 * np.mod(t * f_carrier, 1.0) - 1.0
        if control_mode.upper() == "SQUARE":
            q1 = (np.sin(2.0 * np.pi * f_out * t) >= 0).astype(float)
        else:
            q1 = spwm(t, f_carrier, f_out, m)
        q2 = 1.0 - q1
        q3 = q2
        q4 = q1
        pole_a = (2.0 * q1 - 1.0) * vdc / 2.0
        pole_b = (2.0 * q3 - 1.0) * vdc / 2.0
        vout = pole_a - pole_b
        iout = np.zeros_like(vout)
        for i in range(1, num_points):
            if l_load > 0:
                di = (vout[i - 1] - r_load * iout[i - 1]) / l_load
                iout[i] = iout[i - 1] + dt * di
            else:
                iout[i] = vout[i] / max(r_load, 1e-6)

        vrms = float(np.sqrt(np.mean(vout**2)))
        irms = float(np.sqrt(np.mean(iout**2)))
        pout = float(np.mean(vout * iout))
        pin = pout / 0.96 if pout > 0 else 0.0
        metrics = {
            "Vout_rms": vrms,
            "THD_%": self.compute_THD(vout, f_out, 1.0 / dt),
            "modulation_index_actual": float(np.max(np.abs(ref))),
            "fundamental_V": float(m * vdc / 2.0),
            "output_power_W": pout,
            "efficiency_%": self.compute_efficiency(pin, pout),
        }
        signals = {
            "Vdc": np.full_like(t, vdc),
            "Vout_phase": vout,
            "Iout_phase": iout,
            "switch_states": np.vstack([q1, q2, q3, q4]).T,
            "Vout_fundamental": m * vdc * np.sin(2.0 * np.pi * f_out * t),
            "Vout_harmonics": vout - m * vdc * np.sin(2.0 * np.pi * f_out * t),
            "Vout": vout,
            "Iout": iout,
            "Q1": q1,
            "Q2": q2,
            "Q3": q3,
            "Q4": q4,
            "carrier_wave": carrier,
            "reference_wave": ref,
        }
        return SimulationResult(t, signals, metrics, "single_phase_hbridge", dict(self.params))

    def get_theoretical_values(self) -> dict[str, float]:
        vdc = float(self.params["Vdc"])
        m = float(self.params["modulation_index"])
        return {"fundamental_V": m * vdc / 2.0}

    @staticmethod
    def get_param_schema() -> dict[str, dict[str, float | str]]:
        return {
            "Vdc": {"type": "float", "min": 10.0, "max": 800.0, "step": 1.0, "default": 300.0, "unit": "V", "label": "DC Link Voltage"},
            "f_output": {"type": "float", "min": 1.0, "max": 500.0, "step": 1.0, "default": 50.0, "unit": "Hz", "label": "Output Frequency"},
            "f_carrier": {"type": "float", "min": 100.0, "max": 100000.0, "step": 100.0, "default": 5000.0, "unit": "Hz", "label": "Carrier Frequency"},
            "modulation_index": {"type": "float", "min": 0.0, "max": 1.0, "step": 0.01, "default": 0.8, "unit": "", "label": "Modulation Index"},
            "R_load": {"type": "float", "min": 1.0, "max": 500.0, "step": 1.0, "default": 20.0, "unit": "ohm", "label": "Load Resistance"},
            "L_load": {"type": "float", "min": 0.0, "max": 0.5, "step": 0.001, "default": 0.01, "unit": "H", "label": "Load Inductance"},
            "C_load": {"type": "float", "min": 0.0, "max": 0.01, "step": 0.0001, "default": 0.0, "unit": "F", "label": "Load Capacitance"},
            "control_mode": {"type": "string", "default": "SPWM", "unit": "", "label": "Control Mode"},
        }

    @staticmethod
    def get_info() -> ConverterInfo:
        return ConverterInfo(
            name="Single-Phase H-Bridge VSI",
            category="DC-AC",
            description="Four-switch bridge inverter with SPWM or square-wave modulation.",
            equations=[r"V_{1,peak}=m\frac{V_{dc}}{2}", r"f_1=f_{output}"],
        )
