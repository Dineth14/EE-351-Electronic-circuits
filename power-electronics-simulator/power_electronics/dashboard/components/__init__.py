"""Dashboard component builders for sidebar, waveform, metrics, spectrum, and theory panels."""

from power_electronics.dashboard.components.metrics_panel import metrics_panel
from power_electronics.dashboard.components.sidebar import (
    PARAMETER_PRESETS,
    build_param_controls,
    sidebar_layout,
)
from power_electronics.dashboard.components.spectrum_panel import spectrum_panel
from power_electronics.dashboard.components.theory_panel import theory_panel
from power_electronics.dashboard.components.waveform_panel import waveform_panel

__all__ = [
    "build_param_controls",
    "metrics_panel",
    "PARAMETER_PRESETS",
    "sidebar_layout",
    "spectrum_panel",
    "theory_panel",
    "waveform_panel",
]
