"""Dashboard component builders and layouts."""

from __future__ import annotations

from power_electronics.dashboard.components.sidebar import sidebar_layout
from power_electronics.dashboard.components.waveform_panel import waveform_panel
from power_electronics.dashboard.components.metrics_panel import metrics_panel
from power_electronics.dashboard.components.spectrum_panel import spectrum_panel
from power_electronics.dashboard.components.theory_panel import theory_panel

__all__ = [
    "sidebar_layout",
    "waveform_panel",
    "metrics_panel",
    "spectrum_panel",
    "theory_panel",
]
