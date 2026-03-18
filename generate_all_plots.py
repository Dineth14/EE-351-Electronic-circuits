from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from power_sim import ac_dc, dc_ac, dc_dc, loads, plotter, utils


def _save(fig: plt.Figure, output_dir: Path, name: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / name, dpi=180, bbox_inches="tight")
    plt.close(fig)


def generate_ac_dc(output_dir: Path) -> None:
    f = 50.0
    vm = 325.0
    alpha = np.deg2rad(45.0)
    t = utils.timebase(fundamental_frequency=f, cycles=1.0, samples_per_cycle=5000)
    wt = plotter.to_omega_t(t, f)

    half = ac_dc.single_phase_half_wave_rectifier(t, source_peak=vm, frequency=f, alpha=alpha, controlled=True)
    bridge = ac_dc.single_phase_full_bridge_rectifier(
        t,
        source_peak=vm,
        frequency=f,
        alpha=alpha,
        controlled=True,
        continuous_current=True,
    )
    three = ac_dc.three_phase_bridge_rectifier(t, phase_peak=vm, frequency=f, alpha=0.0, controlled=False)

    fig, _ = plotter.plot_stacked_waveforms(
        wt,
        [
            {"y": half["source_voltage"], "label": "Source", "ylabel": "v_s (V)"},
            {"y": half["output_voltage"], "label": "Half-wave SCR", "ylabel": "v_o (V)"},
            {"y": bridge["output_voltage"], "label": "Full-bridge SCR CCM", "ylabel": "v_o (V)"},
        ],
        xlabel="Electrical angle (rad)",
        title="AC-DC: Single-phase rectifiers",
    )
    _save(fig, output_dir, "ac_dc_single_phase.png")

    va, vb, vc = three["phase_voltages"]
    fig, _ = plotter.plot_stacked_waveforms(
        wt,
        [
            {"y": va, "label": "v_a", "ylabel": "Phase voltage (V)"},
            {"y": vb, "label": "v_b", "ylabel": "Phase voltage (V)"},
            {"y": vc, "label": "v_c", "ylabel": "Phase voltage (V)"},
            {"y": three["output_voltage"], "label": "v_o", "ylabel": "Rectified output (V)"},
        ],
        xlabel="Electrical angle (rad)",
        title="AC-DC: Three-phase six-pulse bridge",
    )
    _save(fig, output_dir, "ac_dc_three_phase_bridge.png")



def generate_dc_ac(output_dir: Path) -> None:
    f = 50.0
    t = utils.timebase(fundamental_frequency=f, cycles=1.0, samples_per_cycle=6000)
    wt = plotter.to_omega_t(t, f)

    sp_bip = dc_ac.single_phase_bipolar_spwm(
        t,
        dc_bus=300.0,
        output_frequency=f,
        carrier_frequency=5000.0,
        modulation_index=0.85,
    )
    sp_uni = dc_ac.single_phase_unipolar_spwm(
        t,
        dc_bus=300.0,
        output_frequency=f,
        carrier_frequency=5000.0,
        modulation_index=0.85,
    )
    three = dc_ac.three_phase_six_step(t, dc_bus=400.0, output_frequency=f, conduction_mode=180)

    fig, _ = plotter.plot_stacked_waveforms(
        wt[:1600],
        [
            {"y": sp_bip["reference"][:1600], "label": "Reference", "ylabel": "Ref/Carrier"},
            {"y": sp_bip["carrier"][:1600], "label": "Carrier", "ylabel": "Ref/Carrier"},
            {"y": sp_bip["output_voltage"][:1600], "label": "Bipolar SPWM", "ylabel": "v_o (V)"},
            {"y": sp_uni["output_voltage"][:1600], "label": "Unipolar SPWM", "ylabel": "v_o (V)"},
        ],
        xlabel="Electrical angle (rad)",
        title="DC-AC: Single-phase SPWM",
    )
    _save(fig, output_dir, "dc_ac_spwm_single_phase.png")

    vab = three["line_voltages"]["v_ab"]
    vbc = three["line_voltages"]["v_bc"]
    vca = three["line_voltages"]["v_ca"]

    star = loads.balanced_three_phase_star_load(
        t,
        phase_voltages=three["phase_voltages"],
        resistance=15.0,
        inductance=0.03,
        settle_cycles=6,
    )
    delta = loads.balanced_three_phase_delta_load(
        t,
        line_voltages=np.vstack([vab, vbc, vca]),
        resistance=15.0,
        inductance=0.03,
        settle_cycles=6,
    )

    fig, _ = plotter.plot_stacked_waveforms(
        wt,
        [
            {"y": vab, "label": "v_ab", "ylabel": "Line voltage (V)"},
            {"y": star.currents_line[0], "label": "i_a (Y-load)", "ylabel": "Line current (A)"},
            {"y": delta.currents_line[0], "label": "i_a (Delta-load)", "ylabel": "Line current (A)"},
        ],
        xlabel="Electrical angle (rad)",
        title="DC-AC: Three-phase load current comparison",
    )
    _save(fig, output_dir, "dc_ac_three_phase_star_vs_delta.png")



def generate_dc_dc(output_dir: Path) -> None:
    vg = 48.0
    d = 0.45
    fs = 40_000.0
    r = 12.0
    l = 180e-6
    c = 220e-6

    ts = 1.0 / fs
    t = np.linspace(0.0, 8.0 * ts, 5000, endpoint=False)

    buck_ccm = dc_dc.buck_converter(t, vg, d, fs, r, l, capacitance=c, mode="CCM")
    boost_ccm = dc_dc.boost_converter(t, vg, d, fs, r, l, capacitance=c, mode="CCM")
    bb_ccm = dc_dc.buck_boost_converter(t, vg, d, fs, r, l, capacitance=c, mode="CCM")

    fig, _ = plotter.plot_stacked_waveforms(
        t * 1e6,
        [
            {"y": buck_ccm["inductor_current"], "label": "Buck i_L", "ylabel": "Current (A)"},
            {"y": boost_ccm["inductor_current"], "label": "Boost i_L", "ylabel": "Current (A)"},
            {"y": bb_ccm["inductor_current"], "label": "Buck-Boost i_L", "ylabel": "Current (A)"},
            {"y": buck_ccm["output_voltage"], "label": "Buck v_o", "ylabel": "Voltage (V)"},
            {"y": boost_ccm["output_voltage"], "label": "Boost v_o", "ylabel": "Voltage (V)"},
            {"y": bb_ccm["output_voltage"], "label": "Buck-Boost v_o", "ylabel": "Voltage (V)"},
        ],
        xlabel="Time (us)",
        title="DC-DC: Buck / Boost / Buck-Boost (CCM)",
        figsize=(12.0, 10.0),
    )
    _save(fig, output_dir, "dc_dc_all_ccm.png")



def main() -> None:
    root = Path(__file__).resolve().parent
    out = root / "outputs" / "plots"

    generate_ac_dc(out)
    generate_dc_ac(out)
    generate_dc_dc(out)

    print(f"Saved plots in: {out}")


if __name__ == "__main__":
    main()
