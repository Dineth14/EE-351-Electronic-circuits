from __future__ import annotations

from dataclasses import dataclass

import numpy as np

try:
    from scipy.integrate import solve_ivp
except Exception:  # pragma: no cover - optional dependency
    solve_ivp = None

try:
    from .utils import rms_value
except ImportError:  # pragma: no cover - direct script execution fallback
    from utils import rms_value


@dataclass
class LoadWaveform:
    """Container for load voltage and current."""

    time: np.ndarray
    voltage: np.ndarray
    current: np.ndarray

    @property
    def average_current(self) -> float:
        return float(np.mean(self.current))

    @property
    def rms_current(self) -> float:
        return rms_value(self.current)

    @property
    def average_power(self) -> float:
        return float(np.mean(self.voltage * self.current))


@dataclass
class ThreePhaseLoadWaveform:
    """Container for balanced three-phase load results."""

    time: np.ndarray
    load_type: str
    voltages_phase: np.ndarray
    currents_phase: np.ndarray
    currents_line: np.ndarray
    branch_currents: np.ndarray | None = None

    @property
    def rms_line_currents(self) -> np.ndarray:
        return np.sqrt(np.mean(np.square(self.currents_line), axis=1))

    @property
    def average_three_phase_power(self) -> float:
        return float(np.mean(np.sum(self.voltages_phase * self.currents_phase, axis=0)))


def _extend_periodic_waveform(
    time: np.ndarray,
    voltage: np.ndarray,
    settle_cycles: int,
) -> tuple[np.ndarray, np.ndarray, slice]:
    if settle_cycles <= 0:
        return time, voltage, slice(None)

    if len(time) < 2:
        return time, voltage, slice(None)

    period = (time[-1] - time[0]) + (time[1] - time[0])
    repeats = int(settle_cycles) + 1
    extended_time = np.concatenate([time + period * index for index in range(repeats)])
    extended_voltage = np.tile(voltage, repeats)
    start = (repeats - 1) * len(time)
    return extended_time, extended_voltage, slice(start, start + len(time))


def _simulate_series_load(
    time: np.ndarray,
    voltage: np.ndarray,
    resistance: float,
    inductance: float = 0.0,
    back_emf: float = 0.0,
    initial_current: float = 0.0,
    allow_negative_current: bool = True,
    settle_cycles: int = 0,
) -> LoadWaveform:
    time = np.asarray(time, dtype=float)
    voltage = np.asarray(voltage, dtype=float)
    sim_time, sim_voltage, keep = _extend_periodic_waveform(time, voltage, settle_cycles)

    current = np.zeros_like(sim_voltage)
    current[0] = float(initial_current)

    if resistance <= 0.0 and inductance <= 0.0:
        raise ValueError("At least one of resistance or inductance must be positive.")

    for index in range(1, len(sim_time)):
        dt = sim_time[index] - sim_time[index - 1]
        drive = sim_voltage[index - 1] - back_emf
        previous = current[index - 1]

        if inductance <= 0.0:
            next_current = drive / resistance
        elif resistance > 0.0:
            steady_current = drive / resistance
            decay = np.exp(-resistance * dt / inductance)
            next_current = steady_current + (previous - steady_current) * decay
        else:
            next_current = previous + drive * dt / inductance

        if not allow_negative_current and next_current < 0.0:
            next_current = 0.0

        current[index] = next_current

    return LoadWaveform(time=time, voltage=voltage, current=current[keep])


def _simulate_series_load_ode(
    time: np.ndarray,
    voltage: np.ndarray,
    resistance: float,
    inductance: float,
    back_emf: float = 0.0,
    initial_current: float = 0.0,
    allow_negative_current: bool = True,
    settle_cycles: int = 0,
) -> LoadWaveform:
    if solve_ivp is None:
        raise ImportError("SciPy is required for method='ode'. Install scipy or use method='analytic'.")

    time = np.asarray(time, dtype=float)
    voltage = np.asarray(voltage, dtype=float)
    sim_time, sim_voltage, keep = _extend_periodic_waveform(time, voltage, settle_cycles)

    def voltage_interp(t_val: float) -> float:
        return float(np.interp(t_val, sim_time, sim_voltage))

    def di_dt(t_val: float, y: np.ndarray) -> np.ndarray:
        drive = voltage_interp(t_val) - back_emf
        if resistance > 0.0:
            return np.array([(drive - resistance * y[0]) / inductance], dtype=float)
        return np.array([drive / inductance], dtype=float)

    solution = solve_ivp(
        fun=di_dt,
        t_span=(float(sim_time[0]), float(sim_time[-1])),
        y0=np.array([float(initial_current)], dtype=float),
        t_eval=sim_time,
        method="RK45",
        rtol=1e-6,
        atol=1e-9,
    )

    if not solution.success:
        raise RuntimeError(f"ODE simulation failed: {solution.message}")

    current = solution.y[0]
    if not allow_negative_current:
        current = np.maximum(current, 0.0)

    return LoadWaveform(time=time, voltage=voltage, current=current[keep])


class ResistiveLoad:
    """Purely resistive load."""

    def __init__(self, resistance: float) -> None:
        if resistance <= 0.0:
            raise ValueError("Resistance must be positive.")
        self.resistance = float(resistance)

    def simulate(self, time: np.ndarray, voltage: np.ndarray) -> LoadWaveform:
        current = np.asarray(voltage, dtype=float) / self.resistance
        return LoadWaveform(time=np.asarray(time, dtype=float), voltage=np.asarray(voltage, dtype=float), current=current)


class RLLoad:
    """Series RL load with optional current clamping for discontinuous conduction."""

    def __init__(self, resistance: float, inductance: float, allow_negative_current: bool = True) -> None:
        if resistance < 0.0 or inductance <= 0.0:
            raise ValueError("Use resistance >= 0 and inductance > 0 for RL loads.")
        self.resistance = float(resistance)
        self.inductance = float(inductance)
        self.allow_negative_current = bool(allow_negative_current)

    def simulate(
        self,
        time: np.ndarray,
        voltage: np.ndarray,
        initial_current: float = 0.0,
        settle_cycles: int = 0,
        method: str = "analytic",
    ) -> LoadWaveform:
        method = method.lower()
        if method == "analytic":
            return _simulate_series_load(
                time=time,
                voltage=voltage,
                resistance=self.resistance,
                inductance=self.inductance,
                initial_current=initial_current,
                allow_negative_current=self.allow_negative_current,
                settle_cycles=settle_cycles,
            )
        if method == "ode":
            return _simulate_series_load_ode(
                time=time,
                voltage=voltage,
                resistance=self.resistance,
                inductance=self.inductance,
                initial_current=initial_current,
                allow_negative_current=self.allow_negative_current,
                settle_cycles=settle_cycles,
            )
        raise ValueError("method must be either 'analytic' or 'ode'.")


class RLELoad:
    """Series RLE load, useful for DC motor armature approximations."""

    def __init__(self, resistance: float, inductance: float, back_emf: float, allow_negative_current: bool = True) -> None:
        if resistance < 0.0 or inductance <= 0.0:
            raise ValueError("Use resistance >= 0 and inductance > 0 for RLE loads.")
        self.resistance = float(resistance)
        self.inductance = float(inductance)
        self.back_emf = float(back_emf)
        self.allow_negative_current = bool(allow_negative_current)

    def simulate(
        self,
        time: np.ndarray,
        voltage: np.ndarray,
        initial_current: float = 0.0,
        settle_cycles: int = 0,
        method: str = "analytic",
    ) -> LoadWaveform:
        method = method.lower()
        if method == "analytic":
            return _simulate_series_load(
                time=time,
                voltage=voltage,
                resistance=self.resistance,
                inductance=self.inductance,
                back_emf=self.back_emf,
                initial_current=initial_current,
                allow_negative_current=self.allow_negative_current,
                settle_cycles=settle_cycles,
            )
        if method == "ode":
            return _simulate_series_load_ode(
                time=time,
                voltage=voltage,
                resistance=self.resistance,
                inductance=self.inductance,
                back_emf=self.back_emf,
                initial_current=initial_current,
                allow_negative_current=self.allow_negative_current,
                settle_cycles=settle_cycles,
            )
        raise ValueError("method must be either 'analytic' or 'ode'.")


class IdealCurrentLoad:
    """Ideal ripple-free current sink or source."""

    def __init__(self, current_level: float) -> None:
        self.current_level = float(current_level)

    def simulate(self, time: np.ndarray, voltage: np.ndarray) -> LoadWaveform:
        current = np.full_like(np.asarray(voltage, dtype=float), self.current_level, dtype=float)
        return LoadWaveform(time=np.asarray(time, dtype=float), voltage=np.asarray(voltage, dtype=float), current=current)


def _line_currents_from_delta_branches(branch_currents: np.ndarray) -> np.ndarray:
    """Compute line currents from delta branch currents [i_ab, i_bc, i_ca]."""
    i_ab, i_bc, i_ca = branch_currents
    i_a = i_ab - i_ca
    i_b = i_bc - i_ab
    i_c = i_ca - i_bc
    return np.vstack([i_a, i_b, i_c])


def balanced_three_phase_star_load(
    time: np.ndarray,
    phase_voltages: np.ndarray,
    resistance: float,
    inductance: float = 0.0,
    initial_currents: tuple[float, float, float] = (0.0, 0.0, 0.0),
    settle_cycles: int = 0,
    method: str = "analytic",
) -> ThreePhaseLoadWaveform:
    """Balanced 3-phase Y-load. Expects phase voltages [v_an, v_bn, v_cn]."""
    phase_voltages = np.asarray(phase_voltages, dtype=float)
    if phase_voltages.shape[0] != 3:
        raise ValueError("phase_voltages must have shape (3, N).")

    currents_phase = np.zeros_like(phase_voltages)
    for idx in range(3):
        if inductance > 0.0:
            load = RLLoad(resistance=resistance, inductance=inductance)
            wave = load.simulate(
                time=time,
                voltage=phase_voltages[idx],
                initial_current=initial_currents[idx],
                settle_cycles=settle_cycles,
                method=method,
            )
            currents_phase[idx] = wave.current
        else:
            load = ResistiveLoad(resistance=resistance)
            wave = load.simulate(time=time, voltage=phase_voltages[idx])
            currents_phase[idx] = wave.current

    return ThreePhaseLoadWaveform(
        time=np.asarray(time, dtype=float),
        load_type="star",
        voltages_phase=phase_voltages,
        currents_phase=currents_phase,
        currents_line=currents_phase.copy(),
    )


def balanced_three_phase_delta_load(
    time: np.ndarray,
    line_voltages: np.ndarray,
    resistance: float,
    inductance: float = 0.0,
    initial_branch_currents: tuple[float, float, float] = (0.0, 0.0, 0.0),
    settle_cycles: int = 0,
    method: str = "analytic",
) -> ThreePhaseLoadWaveform:
    """Balanced 3-phase Delta-load. Expects line voltages [v_ab, v_bc, v_ca]."""
    line_voltages = np.asarray(line_voltages, dtype=float)
    if line_voltages.shape[0] != 3:
        raise ValueError("line_voltages must have shape (3, N).")

    branch_currents = np.zeros_like(line_voltages)
    for idx in range(3):
        if inductance > 0.0:
            load = RLLoad(resistance=resistance, inductance=inductance)
            wave = load.simulate(
                time=time,
                voltage=line_voltages[idx],
                initial_current=initial_branch_currents[idx],
                settle_cycles=settle_cycles,
                method=method,
            )
            branch_currents[idx] = wave.current
        else:
            load = ResistiveLoad(resistance=resistance)
            wave = load.simulate(time=time, voltage=line_voltages[idx])
            branch_currents[idx] = wave.current

    currents_line = _line_currents_from_delta_branches(branch_currents)
    # For an equivalent per-phase representation in delta, map branch currents as phase currents.
    currents_phase = branch_currents

    return ThreePhaseLoadWaveform(
        time=np.asarray(time, dtype=float),
        load_type="delta",
        voltages_phase=line_voltages,
        currents_phase=currents_phase,
        currents_line=currents_line,
        branch_currents=branch_currents,
    )
