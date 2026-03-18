"""Dual Active Bridge converter model."""

from __future__ import annotations

import numpy as np

from power_electronics.converters.dc_dc._common import DCDCBaseConverter
from power_electronics.core.base_converter import ConverterInfo, SimulationResult
from power_electronics.core.simulation_engine import generate_switch_state


class DualActiveBridgeConverter(DCDCBaseConverter):
    """Bidirectional isolated converter using phase-shift control."""

    converter_name = "dual_active_bridge"

    def simulate(self, t_end: float, num_points: int) -> SimulationResult:
        p = self.params
        vin = float(p["Vin"])
        duty = float(p["duty_cycle"])
        fs = float(p["frequency"])
        l_tank = float(p["L"])
        c_val = float(p["C"])
        r_load = float(p["R_load"])
        phase_shift = float(p.get("phase_shift", 0.25))

        t = np.linspace(0.0, t_end, num_points)
        dt = t[1] - t[0]
        q_primary = generate_switch_state(t, fs, 0.5)
        q_secondary = generate_switch_state(t + phase_shift / fs, fs, 0.5)
        v_ab1 = vin * (2.0 * q_primary - 1.0)
        v_ab2 = vin * (2.0 * q_secondary - 1.0) * duty
        il_tank = np.zeros(num_points)
        vout = np.zeros(num_points)

        for i in range(1, num_points):
            dil = (v_ab1[i - 1] - v_ab2[i - 1]) / max(l_tank, 1e-9)
            il_tank[i] = il_tank[i - 1] + dt * dil
            i_out = vout[i - 1] / max(r_load, 1e-6)
            dv = (duty * abs(il_tank[i - 1]) - i_out) / max(c_val, 1e-9)
            vout[i] = max(0.0, vout[i - 1] + dt * dv)

        iout = vout / max(r_load, 1e-6)
        pin = float(np.mean(np.abs(v_ab1 * il_tank)))
        pout = float(np.mean(vout * iout))
        signals = {
            "Vin": np.full_like(t, vin),
            "Vout": vout,
            "IL_tank": il_tank,
            "Q1": q_primary,
            "Q2": 1.0 - q_primary,
            "Q3": q_primary,
            "Q4": 1.0 - q_primary,
            "Q5": q_secondary,
            "Q6": 1.0 - q_secondary,
            "Q7": q_secondary,
            "Q8": 1.0 - q_secondary,
            "phase_shift": np.full_like(t, phase_shift),
        }
        metrics = {
            "Vout_avg": float(np.mean(vout)),
            "Vout_ripple_%": self.compute_ripple(vout),
            "IL_ripple_A": float(np.max(il_tank) - np.min(il_tank)),
            "efficiency_%": self.compute_efficiency(pin, pout),
            "input_power_W": pin,
            "output_power_W": pout,
            "duty_cycle_actual": 0.5,
        }
        return SimulationResult(t, signals, metrics, self.converter_name, dict(self.params))

    def get_theoretical_values(self) -> dict[str, float]:
        vin = float(self.params["Vin"])
        phi = float(self.params.get("phase_shift", 0.25))
        return {"power_transfer_pu": phi * (1.0 - phi), "Vout_avg": vin * float(self.params["duty_cycle"])}

    @staticmethod
    def get_param_schema() -> dict[str, dict[str, float | str]]:
        schema = DualActiveBridgeConverter._base_schema()
        schema["phase_shift"] = {
            "type": "float",
            "min": 0.0,
            "max": 0.49,
            "step": 0.01,
            "default": 0.25,
            "unit": "pu",
            "label": "Phase Shift",
        }
        return schema

    @staticmethod
    def get_info() -> ConverterInfo:
        return ConverterInfo(
            name="Dual Active Bridge",
            category="DC-DC",
            description="Bidirectional isolated converter controlled by bridge phase shift.",
            equations=[r"P\propto \phi(1-\phi)\frac{V_1V_2}{\omega L}"],
        )
