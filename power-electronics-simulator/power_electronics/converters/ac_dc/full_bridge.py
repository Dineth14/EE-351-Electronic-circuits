"""Single-phase full-bridge diode rectifier."""

from __future__ import annotations

import numpy as np

from power_electronics.converters.ac_dc.full_wave_centertap import FullWaveCenterTapRectifier
from power_electronics.converters.ac_dc.half_wave import _rc_filter
from power_electronics.core.base_converter import ConverterInfo, SimulationResult


class FullBridgeRectifier(FullWaveCenterTapRectifier):
    """Single-phase bridge rectifier with four diodes."""

    def simulate(self, t_end: float, num_points: int) -> SimulationResult:
        p = self.params
        vm = float(p["Vac_peak"])
        f = float(p["frequency"])
        r = float(p["R_load"])
        c = float(p.get("C_filter", 0.0))
        t = np.linspace(0.0, t_end, num_points)
        dt = t[1] - t[0]
        vac = vm * np.sin(2.0 * np.pi * f * t)
        v_raw = np.abs(vac)
        v_f = _rc_filter(v_raw, dt, r, c) if c > 0 else v_raw
        i_load = v_f / max(r, 1e-6)
        id1 = (vac >= 0).astype(float) * i_load
        id2 = id1.copy()
        id3 = (vac < 0).astype(float) * i_load
        id4 = id3.copy()
        il = np.gradient(v_f, dt) * float(p.get("L_filter", 0.0))
        ic = np.gradient(v_f, dt) * c

        signals = {
            "Vac": vac,
            "Vdc_raw": v_raw,
            "Vdc_filtered": v_f,
            "Iload": i_load,
            "diode_states": np.vstack([id1 > 0, id2 > 0, id3 > 0, id4 > 0]).T.astype(float),
            "Iripple": i_load - np.mean(i_load),
            "Vripple": v_f - np.mean(v_f),
            "Vout_raw": v_raw,
            "Vout_filtered": v_f,
            "ID1": id1,
            "ID2": id2,
            "ID3": id3,
            "ID4": id4,
            "IL": il,
            "IC": ic,
        }
        pin = float(np.mean(np.abs(vac * (id1 + id3))))
        pout = float(np.mean(v_f * i_load))
        metrics = {
            "Vdc_avg": float(np.mean(v_f)),
            "Vdc_rms": float(np.sqrt(np.mean(v_f**2))),
            "Vripple_%": self.compute_ripple(v_f),
            "PIV": float(vm),
            "THD_%": self.compute_THD(v_f, f, 1.0 / dt),
            "power_factor": float(np.mean(vac * (id1 + id3)) / (np.sqrt(np.mean(vac**2)) * np.sqrt(np.mean((id1 + id3) ** 2)) + 1e-12)),
            "efficiency_%": self.compute_efficiency(pin, pout),
        }
        return SimulationResult(t, signals, metrics, "full_bridge", dict(self.params))

    @staticmethod
    def get_info() -> ConverterInfo:
        return ConverterInfo(
            name="1-Phase Full-Bridge Rectifier",
            category="AC-DC",
            description="Bridge of four diodes rectifies both half cycles without center-tap transformer.",
            equations=[r"V_{dc,avg}=\frac{2V_m}{\pi}", r"\text{PIV}=V_m"],
        )
