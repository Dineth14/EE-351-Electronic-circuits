"""Abstract base class definitions for converter simulation objects."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np

from power_electronics.core.analysis import compute_efficiency, compute_ripple, compute_thd


@dataclass(slots=True)
class ConverterInfo:
    """Metadata container for theory and UI rendering.

    Parameters
    ----------
    name:
        Human-readable converter name.
    category:
        Converter category such as AC-DC, DC-DC, or DC-AC.
    description:
        Operating principle summary.
    equations:
        LaTeX equations used in theory panel.
    """

    name: str
    category: str
    description: str
    equations: list[str]


@dataclass(slots=True)
class SimulationResult:
    """Container for simulation outputs.

    Parameters
    ----------
    time:
        Time vector in seconds.
    signals:
        Signal dictionary keyed by signal name.
    metrics:
        Scalar simulation metrics.
    converter_name:
        Converter identifier.
    params:
        Simulation parameters used for this run.
    """

    time: np.ndarray
    signals: dict[str, np.ndarray]
    metrics: dict[str, float]
    converter_name: str
    params: dict[str, float | str]


class BaseConverter(ABC):
    """Abstract base class for all converter models."""

    def __init__(self, params: dict[str, float | str]) -> None:
        self.params = params

    @abstractmethod
    def simulate(self, t_end: float, num_points: int) -> SimulationResult:
        """Run time-domain simulation and return a result object."""

    @abstractmethod
    def get_theoretical_values(self) -> dict[str, float]:
        """Return closed-form theoretical references for validation."""

    @staticmethod
    @abstractmethod
    def get_param_schema() -> dict[str, dict[str, float | str]]:
        """Return JSON-schema style parameter metadata for UI auto-generation."""

    @staticmethod
    @abstractmethod
    def get_info() -> ConverterInfo:
        """Return converter metadata for the theory tab."""

    @staticmethod
    def compute_efficiency(pin: float, pout: float) -> float:
        """Compute efficiency in percent from input and output powers."""
        return compute_efficiency(pin, pout)

    @staticmethod
    def compute_THD(signal: np.ndarray, f0: float, fs: float) -> float:
        """Compute total harmonic distortion in percent."""
        return compute_thd(signal, f0, fs)

    @staticmethod
    def compute_ripple(signal: np.ndarray) -> float:
        """Compute ripple percentage relative to DC value."""
        return compute_ripple(signal)
