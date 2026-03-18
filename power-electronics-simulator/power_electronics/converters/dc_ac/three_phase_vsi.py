"""Three-phase voltage source inverter model."""

from __future__ import annotations

import numpy as np

from power_electronics.core.base_converter import BaseConverter, ConverterInfo, SimulationResult
from power_electronics.core.signal_generator import spwm


class ThreePhaseVSI(BaseConverter):
    """Three-phase two-level inverter with SPWM/180/120 operation modes."""

    def simulate(self, t_end: float, num_points: int) -> SimulationResult:
        p = self.params
        vdc = float(p["Vdc"])
        f_out = float(p["f_output"])
        f_carrier = float(p["f_carrier"])
        m = float(p["modulation_index"])
        r_load = float(p["R_load"])
        l_load = float(p.get("L_load", 0.0))
        control = str(p.get("control_mode", "SPWM")).upper()

        t = np.linspace(0.0, t_end, num_points)
        dt = t[1] - t[0]
        theta = 2.0 * np.pi * f_out * t
        refs = [m * np.sin(theta), m * np.sin(theta - 2.0 * np.pi / 3.0), m * np.sin(theta + 2.0 * np.pi / 3.0)]

        if control == "SPWM" or control == "SVM":
            qa = spwm(t, f_carrier, f_out, m)
            qb = spwm(t - 1.0 / (3.0 * f_out), f_carrier, f_out, m)
            qc = spwm(t + 1.0 / (3.0 * f_out), f_carrier, f_out, m)
        elif control == "120":
            qa = ((np.mod(theta, 2.0 * np.pi) < 2.0 * np.pi / 3.0)).astype(float)
            qb = ((np.mod(theta - 2.0 * np.pi / 3.0, 2.0 * np.pi) < 2.0 * np.pi / 3.0)).astype(float)
            qc = ((np.mod(theta + 2.0 * np.pi / 3.0, 2.0 * np.pi) < 2.0 * np.pi / 3.0)).astype(float)
        else:
            qa = (np.sin(theta) >= 0).astype(float)
            qb = (np.sin(theta - 2.0 * np.pi / 3.0) >= 0).astype(float)
            qc = (np.sin(theta + 2.0 * np.pi / 3.0) >= 0).astype(float)

        va = (2.0 * qa - 1.0) * vdc / 2.0
        vb = (2.0 * qb - 1.0) * vdc / 2.0
        vc = (2.0 * qc - 1.0) * vdc / 2.0
        vab = va - vb
        vbc = vb - vc
        vca = vc - va

        ia = np.zeros_like(va)
        ib = np.zeros_like(vb)
        ic = np.zeros_like(vc)
        for i in range(1, num_points):
            if l_load > 0:
                ia[i] = ia[i - 1] + dt * (va[i - 1] - r_load * ia[i - 1]) / l_load
                ib[i] = ib[i - 1] + dt * (vb[i - 1] - r_load * ib[i - 1]) / l_load
                ic[i] = ic[i - 1] + dt * (vc[i - 1] - r_load * ic[i - 1]) / l_load
            else:
                ia[i] = va[i] / max(r_load, 1e-6)
                ib[i] = vb[i] / max(r_load, 1e-6)
                ic[i] = vc[i] / max(r_load, 1e-6)

        v_fund = m * vdc / 2.0 * np.sin(theta)
        p_out = float(np.mean(va * ia + vb * ib + vc * ic))
        p_in = p_out / 0.97 if p_out > 0 else 0.0
        metrics = {
            "Vout_rms": float(np.sqrt(np.mean(vab**2))),
            "THD_%": self.compute_THD(vab, f_out, 1.0 / dt),
            "modulation_index_actual": float(np.max(np.abs(refs[0]))),
            "fundamental_V": float(np.sqrt(2.0) * np.sqrt(np.mean(v_fund**2))),
            "output_power_W": p_out,
            "efficiency_%": self.compute_efficiency(p_in, p_out),
        }
        signals = {
            "Vdc": np.full_like(t, vdc),
            "Vout_phase_A": va,
            "Vout_phase_B": vb,
            "Vout_phase_C": vc,
            "Iout_phase_A": ia,
            "Iout_phase_B": ib,
            "Iout_phase_C": ic,
            "switch_states": np.vstack([qa, 1 - qa, qb, 1 - qb, qc, 1 - qc]).T,
            "Vout_line": np.vstack([vab, vbc, vca]).T,
            "Vout_fundamental": v_fund,
            "Vout_harmonics": vab - v_fund,
            "Va": va,
            "Vb": vb,
            "Vc": vc,
            "Vab": vab,
            "Vbc": vbc,
            "Vca": vca,
            "Ia": ia,
            "Ib": ib,
            "Ic": ic,
            "Q1": qa,
            "Q2": 1 - qa,
            "Q3": qb,
            "Q4": 1 - qb,
            "Q5": qc,
            "Q6": 1 - qc,
        }
        return SimulationResult(t, signals, metrics, "three_phase_vsi", dict(self.params))

    def get_theoretical_values(self) -> dict[str, float]:
        vdc = float(self.params["Vdc"])
        m = float(self.params["modulation_index"])
        return {"fundamental_phase_peak": m * vdc / 2.0}

    @staticmethod
    def get_param_schema() -> dict[str, dict[str, float | str]]:
        schema = dict(SinglePhaseSchema)
        schema["control_mode"]["default"] = "SPWM"
        return schema

    @staticmethod
    def get_info() -> ConverterInfo:
        return ConverterInfo(
            name="Three-Phase VSI",
            category="DC-AC",
            description="Six-switch inverter with SPWM, 180-degree, and 120-degree modes.",
            equations=[r"V_{LL,1,rms}=0.612mV_{dc}"],
        )


SinglePhaseSchema = {
    "Vdc": {"type": "float", "min": 10.0, "max": 1200.0, "step": 1.0, "default": 600.0, "unit": "V", "label": "DC Link Voltage"},
    "f_output": {"type": "float", "min": 1.0, "max": 500.0, "step": 1.0, "default": 50.0, "unit": "Hz", "label": "Output Frequency"},
    "f_carrier": {"type": "float", "min": 100.0, "max": 100000.0, "step": 100.0, "default": 10000.0, "unit": "Hz", "label": "Carrier Frequency"},
    "modulation_index": {"type": "float", "min": 0.0, "max": 1.0, "step": 0.01, "default": 0.9, "unit": "", "label": "Modulation Index"},
    "R_load": {"type": "float", "min": 1.0, "max": 500.0, "step": 1.0, "default": 15.0, "unit": "ohm", "label": "Load Resistance"},
    "L_load": {"type": "float", "min": 0.0, "max": 0.5, "step": 0.001, "default": 0.02, "unit": "H", "label": "Load Inductance"},
    "C_load": {"type": "float", "min": 0.0, "max": 0.01, "step": 0.0001, "default": 0.0, "unit": "F", "label": "Load Capacitance"},
    "control_mode": {"type": "string", "default": "SPWM", "unit": "", "label": "Control Mode"},
}
