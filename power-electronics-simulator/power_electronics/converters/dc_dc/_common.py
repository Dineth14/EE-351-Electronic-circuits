"""Shared DC-DC simulation utilities."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np

from power_electronics.core.base_converter import BaseConverter, SimulationResult
from power_electronics.core.simulation_engine import detect_conduction_mode, generate_switch_state


DEFAULT_SCHEMA = {
    "Vin": {"type": "float", "min": 1.0, "max": 600.0, "step": 1.0, "default": 48.0, "unit": "V", "label": "Input Voltage"},
    "duty_cycle": {"type": "float", "min": 0.01, "max": 0.99, "step": 0.01, "default": 0.5, "unit": "", "label": "Duty Cycle"},
    "frequency": {"type": "float", "min": 100.0, "max": 1e6, "step": 100.0, "default": 20000.0, "unit": "Hz", "label": "Switching Frequency"},
    "L": {"type": "float", "min": 1e-6, "max": 0.1, "step": 1e-5, "default": 1e-3, "unit": "H", "label": "Inductance"},
    "C": {"type": "float", "min": 1e-7, "max": 0.1, "step": 1e-6, "default": 220e-6, "unit": "F", "label": "Capacitance"},
    "R_load": {"type": "float", "min": 0.5, "max": 500.0, "step": 0.5, "default": 10.0, "unit": "ohm", "label": "Load Resistance"},
    "R_L": {"type": "float", "min": 0.0, "max": 2.0, "step": 0.001, "default": 0.05, "unit": "ohm", "label": "Inductor ESR"},
}


class DCDCBaseConverter(BaseConverter):
    """Base helper for two-state switched DC-DC converters."""

    converter_name = "dc_dc"

    def _simulate_two_state(
        self,
        t_end: float,
        num_points: int,
        on_state: Callable[[float, float], tuple[float, float]],
        off_state: Callable[[float, float], tuple[float, float]],
    ) -> tuple[np.ndarray, dict[str, np.ndarray], dict[str, float]]:
        p = self.params
        vin = float(p["Vin"])
        duty = float(p["duty_cycle"])
        freq = float(p["frequency"])
        l_val = float(p["L"])
        c_val = float(p["C"])
        r_load = float(p["R_load"])

        t = np.linspace(0.0, t_end, num_points)
        dt = t[1] - t[0]
        q = generate_switch_state(t, freq, duty)
        il = np.zeros(num_points)
        vout = np.zeros(num_points)

        for i in range(1, num_points):
            if q[i - 1] > 0.5:
                dil, dv = on_state(il[i - 1], vout[i - 1])
            else:
                dil, dv = off_state(il[i - 1], vout[i - 1])
            il[i] = max(0.0, il[i - 1] + dt * dil)
            vout[i] = vout[i - 1] + dt * dv

        iout = vout / max(r_load, 1e-6)
        ic = c_val * np.gradient(vout, dt)
        d_current = np.where(q < 0.5, il, 0.0)
        p_in = vin * np.mean(q * il)
        p_out = np.mean(vout * iout)
        p_loss = max(0.0, p_in - p_out)
        mode = detect_conduction_mode(il)

        signals = {
            "Vin": np.full_like(t, vin),
            "Vout": vout,
            "IL": il,
            "IC": ic,
            "Iout": iout,
            "switch_Q": q,
            "Q_gate": q,
            "diode_current": d_current,
            "D_current": d_current,
            "power_dissipation": np.full_like(t, p_loss),
        }
        metrics = {
            "Vout_avg": float(np.mean(vout)),
            "Vout_ripple_%": self.compute_ripple(vout),
            "IL_ripple_A": float(np.max(il) - np.min(il)),
            "efficiency_%": self.compute_efficiency(float(p_in), float(p_out)),
            "input_power_W": float(p_in),
            "output_power_W": float(p_out),
            "duty_cycle_actual": float(np.mean(q)),
            "conduction_mode": 1.0 if mode == "CCM" else 0.0,
        }
        return t, signals, metrics

    @staticmethod
    def _base_schema() -> dict[str, dict[str, float | str]]:
        return dict(DEFAULT_SCHEMA)

    def _result(
        self,
        t: np.ndarray,
        signals: dict[str, np.ndarray],
        metrics: dict[str, float],
    ) -> SimulationResult:
        return SimulationResult(t, signals, metrics, self.converter_name, dict(self.params))
