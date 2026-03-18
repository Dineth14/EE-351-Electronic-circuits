"""Publication-quality plot themes with dataclass-based theme definitions.

Three visual profiles suitable for dashboards, publications, and lab use:
- **oscilloscope**: Phosphor-green on black, oscilloscope CRT aesthetic
- **dark**: Engineering dark mode with blue accent
- **light**: Clean white-paper style for printed reports
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ThemeColors:
    """Complete color specification for a visual theme."""

    paper_bgcolor: str
    plot_bgcolor: str
    font_color: str
    grid_color: str
    accent: str
    accent_secondary: str
    text_secondary: str
    border_color: str
    card_bgcolor: str
    success: str
    warning: str
    danger: str
    trace_colors: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ThemeTypography:
    """Font specifications for a theme."""

    family: str = "'JetBrains Mono', 'Fira Code', 'Consolas', monospace"
    size_title: int = 14
    size_axis: int = 11
    size_tick: int = 10
    size_annotation: int = 9


@dataclass(frozen=True, slots=True)
class ThemeLayout:
    """Layout constants for figure styling."""

    margin: dict = field(default_factory=lambda: {"l": 55, "r": 20, "t": 45, "b": 40})
    grid_width: float = 0.5
    grid_dash: str = "dot"
    line_width: float = 1.5
    marker_size: int = 5
    bar_opacity: float = 0.85


@dataclass(frozen=True, slots=True)
class Theme:
    """Complete theme definition combining colors, typography, and layout."""

    name: str
    display_name: str
    colors: ThemeColors
    typography: ThemeTypography = field(default_factory=ThemeTypography)
    layout: ThemeLayout = field(default_factory=ThemeLayout)


# ---------------------------------------------------------------------------
# Theme Definitions
# ---------------------------------------------------------------------------

OSCILLOSCOPE_THEME = Theme(
    name="oscilloscope",
    display_name="Oscilloscope",
    colors=ThemeColors(
        paper_bgcolor="#050508",
        plot_bgcolor="#07090d",
        font_color="#9ef5c8",
        grid_color="#0f2a1e",
        accent="#00ff88",
        accent_secondary="#00ccff",
        text_secondary="#5a8a6e",
        border_color="#133126",
        card_bgcolor="#080c10",
        success="#00ff88",
        warning="#ffd700",
        danger="#ff3860",
        trace_colors=(
            "#00ff88", "#00ccff", "#ff6b9d", "#ffd700",
            "#a78bfa", "#fb923c", "#34d399", "#f472b6",
            "#60a5fa", "#facc15",
        ),
    ),
    typography=ThemeTypography(
        family="'JetBrains Mono', 'Fira Code', 'Consolas', monospace",
    ),
    layout=ThemeLayout(grid_dash="dot", grid_width=0.4, line_width=1.8),
)

DARK_THEME = Theme(
    name="dark",
    display_name="Dark Engineering",
    colors=ThemeColors(
        paper_bgcolor="#0a0a0f",
        plot_bgcolor="#11131a",
        font_color="#e6f1ff",
        grid_color="#2d3345",
        accent="#3b82f6",
        accent_secondary="#8b5cf6",
        text_secondary="#7a8ca5",
        border_color="#23324a",
        card_bgcolor="#0f1521",
        success="#22c55e",
        warning="#eab308",
        danger="#ef4444",
        trace_colors=(
            "#3b82f6", "#ef4444", "#22c55e", "#eab308",
            "#a855f7", "#f97316", "#06b6d4", "#ec4899",
            "#84cc16", "#14b8a6",
        ),
    ),
    typography=ThemeTypography(
        family="'Inter', 'Segoe UI', -apple-system, sans-serif",
    ),
    layout=ThemeLayout(grid_dash="dot", grid_width=0.5, line_width=1.5),
)

LIGHT_THEME = Theme(
    name="light",
    display_name="Light Paper",
    colors=ThemeColors(
        paper_bgcolor="#f8fafc",
        plot_bgcolor="#ffffff",
        font_color="#0f172a",
        grid_color="#e2e8f0",
        accent="#0ea5e9",
        accent_secondary="#7c3aed",
        text_secondary="#64748b",
        border_color="#cbd5e1",
        card_bgcolor="#ffffff",
        success="#16a34a",
        warning="#ca8a04",
        danger="#dc2626",
        trace_colors=(
            "#0ea5e9", "#dc2626", "#16a34a", "#ca8a04",
            "#7c3aed", "#ea580c", "#0891b2", "#db2777",
            "#65a30d", "#0d9488",
        ),
    ),
    typography=ThemeTypography(
        family="'Inter', 'Helvetica Neue', Arial, sans-serif",
        size_title=15,
        size_axis=12,
        size_tick=11,
    ),
    layout=ThemeLayout(grid_dash="solid", grid_width=0.3, line_width=1.4),
)

# ---------------------------------------------------------------------------
# Registry — keyed by theme name for dashboard dropdown lookup
# ---------------------------------------------------------------------------

THEME_REGISTRY: dict[str, Theme] = {
    "oscilloscope": OSCILLOSCOPE_THEME,
    "dark": DARK_THEME,
    "light": LIGHT_THEME,
}

# Backward-compatible flat dict for existing code that accesses THEMES[name]
THEMES: dict[str, dict[str, str]] = {
    name: {
        "paper_bgcolor": th.colors.paper_bgcolor,
        "plot_bgcolor": th.colors.plot_bgcolor,
        "font_color": th.colors.font_color,
        "grid_color": th.colors.grid_color,
        "accent": th.colors.accent,
    }
    for name, th in THEME_REGISTRY.items()
}


def get_theme(name: str) -> Theme:
    """Look up a theme by name, defaulting to oscilloscope."""
    return THEME_REGISTRY.get(name, OSCILLOSCOPE_THEME)


def get_trace_color(theme: Theme, index: int) -> str:
    """Get a trace color by index, cycling through available colors."""
    colors = theme.colors.trace_colors
    if not colors:
        return theme.colors.accent
    return colors[index % len(colors)]
