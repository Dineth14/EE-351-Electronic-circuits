"""Publication-quality theme system for dashboard visualization.

Three complete themes:
  1. OSCILLOSCOPE - Lab instrument aesthetic (green-on-black)
  2. DARK_ENGINEERING - Modern dark engineering theme (purple-blue)
  3. LIGHT_PAPER - Publication/paper quality (high contrast, B&W compatible)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    """Complete visual theme definition.

    Parameters
    ----------
    name:
        Theme identifier.
    bg_primary:
        Main background color (hex).
    bg_secondary:
        Panel/card background color (hex).
    bg_plot:
        Plot area background color (hex).
    grid_color:
        Plot grid line color (hex or rgba).
    text_primary:
        Primary text color (hex).
    text_secondary:
        Secondary/muted text color (hex).
    accent_1:
        Primary accent color (hex).
    accent_2:
        Secondary accent color (hex).
    accent_3:
        Tertiary accent color (hex).
    signal_colors:
        List of 12 distinct colors for signal traces.
    good_color:
        Color for good metric threshold (hex).
    warn_color:
        Color for warning metric threshold (hex).
    danger_color:
        Color for danger/critical metric threshold (hex).
    """

    name: str
    bg_primary: str
    bg_secondary: str
    bg_plot: str
    grid_color: str
    text_primary: str
    text_secondary: str
    accent_1: str
    accent_2: str
    accent_3: str
    signal_colors: list[str]
    good_color: str
    warn_color: str
    danger_color: str

    def to_plotly_template(self) -> dict[str, str | int | float]:
        """Convert to Plotly layout template dictionary."""
        return {
            "background_color": self.bg_plot,
            "font_color": self.text_primary,
            "grid_color": self.grid_color,
            "accent_color": self.accent_1,
        }

    def to_css_variables(self) -> dict[str, str]:
        """Generate CSS custom properties for dashboard styling."""
        return {
            "--bg-primary": self.bg_primary,
            "--bg-secondary": self.bg_secondary,
            "--bg-plot": self.bg_plot,
            "--grid-color": self.grid_color,
            "--text-primary": self.text_primary,
            "--text-secondary": self.text_secondary,
            "--accent-1": self.accent_1,
            "--accent-2": self.accent_2,
            "--accent-3": self.accent_3,
            "--good-color": self.good_color,
            "--warn-color": self.warn_color,
            "--danger-color": self.danger_color,
        }


# ==============================================================================
# THEME 1: OSCILLOSCOPE
# ==============================================================================
# Lab instrument aesthetic inspired by analog oscilloscopes.
# Green phosphor display on black (classic CRT look).
# Excellent for technical presentations and dark environments.
# ==============================================================================

OSCILLOSCOPE = Theme(
    name="Oscilloscope",
    bg_primary="#050a05",
    bg_secondary="#0a140a",
    bg_plot="#050a05",
    grid_color="rgba(0,255,80,0.12)",
    text_primary="#00ff50",
    text_secondary="#00aa35",
    accent_1="#00ff50",
    accent_2="#ffcc00",
    accent_3="#ff5500",
    signal_colors=[
        "#00ff50",  # Bright green
        "#ffcc00",  # Yellow
        "#00ccff",  # Cyan
        "#ff5500",  # Orange
        "#ff00ff",  # Magenta
        "#ffffff",  # White
        "#ff9900",  # Light orange
        "#00ffff",  # Aqua
        "#ff0055",  # Hot pink
        "#aaff00",  # Lime
        "#aa00ff",  # Violet
        "#ff6680",  # Coral
    ],
    good_color="#00ff50",
    warn_color="#ffcc00",
    danger_color="#ff3300",
)

# ==============================================================================
# THEME 2: DARK ENGINEERING
# ==============================================================================
# Modern dark theme with engineering aesthetics.
# Purple-blue color scheme with high contrast.
# Best for long work sessions and eye comfort.
# ==============================================================================

DARK_ENGINEERING = Theme(
    name="Dark Engineering",
    bg_primary="#0d0d14",
    bg_secondary="#13131e",
    bg_plot="#0a0a10",
    grid_color="rgba(100,120,255,0.1)",
    text_primary="#e8eaf6",
    text_secondary="#9fa8da",
    accent_1="#7c83ff",
    accent_2="#00e5ff",
    accent_3="#ff6e40",
    signal_colors=[
        "#7c83ff",  # Indigo
        "#00e5ff",  # Light blue
        "#69ff47",  # Light green
        "#ff6e40",  # Deep orange
        "#ffd740",  # Amber
        "#ea80fc",  # Light purple
        "#64ffda",  # Cyan
        "#ff4081",  # Pink
        "#40c4ff",  # Light cyan
        "#ccff90",  # Lime green
        "#ffab40",  # Orange
        "#b388ff",  # Light purple
    ],
    good_color="#69ff47",
    warn_color="#ffd740",
    danger_color="#ff1744",
)

# ==============================================================================
# THEME 3: LIGHT / PAPER
# ==============================================================================
# Publication quality theme for printed reports and presentations.
# High contrast, B&W compatible, suits traditional academic environment.
# Excellent for colorblind-friendly output.
# ==============================================================================

LIGHT_PAPER = Theme(
    name="Light / Paper",
    bg_primary="#fafafa",
    bg_secondary="#ffffff",
    bg_plot="#ffffff",
    grid_color="rgba(0,0,0,0.08)",
    text_primary="#212121",
    text_secondary="#616161",
    accent_1="#1565c0",
    accent_2="#c62828",
    accent_3="#2e7d32",
    signal_colors=[
        "#1565c0",  # Deep blue
        "#c62828",  # Deep red
        "#2e7d32",  # Deep green
        "#6a1b9a",  # Deep purple
        "#e65100",  # Deep orange
        "#00838f",  # Teal
        "#558b2f",  # Dark green
        "#4527a0",  # Indigo
        "#ad1457",  # Pink
        "#0277bd",  # Light blue
        "#37474f",  # Blue grey
        "#f57f17",  # Amber
    ],
    good_color="#2e7d32",
    warn_color="#f57c00",
    danger_color="#c62828",
)

# ==============================================================================
# THEME REGISTRY
# ==============================================================================

THEME_REGISTRY: dict[str, Theme] = {
    "oscilloscope": OSCILLOSCOPE,
    "dark_engineering": DARK_ENGINEERING,
    "light_paper": LIGHT_PAPER,
}

DEFAULT_THEME = OSCILLOSCOPE


def get_theme(name: str) -> Theme:
    """Retrieve theme by name.

    Parameters
    ----------
    name:
        Theme identifier (case-insensitive).

    Returns
    -------
    Theme
        The requested theme, or DEFAULT_THEME if not found.
    """
    return THEME_REGISTRY.get(name.lower(), DEFAULT_THEME)


def list_themes() -> list[str]:
    """Return list of available theme names."""
    return list(THEME_REGISTRY.keys())
