"""Tests for converter registry completeness and theme system."""

from __future__ import annotations

import numpy as np
import pytest

from power_electronics.converters import CONVERTER_REGISTRY
from power_electronics.visualization.themes import (
    THEME_REGISTRY,
    THEMES,
    Theme,
    get_theme,
    get_trace_color,
)


# ---------------------------------------------------------------------------
# Registry Tests
# ---------------------------------------------------------------------------

class TestConverterRegistry:
    def test_registry_has_all_converters(self):
        expected = {
            "half_wave", "full_wave_centertap", "full_bridge",
            "three_phase_half", "three_phase_bridge",
            "scr_half_wave", "scr_full_bridge", "vienna_rectifier",
            "single_phase_hbridge", "three_phase_vsi",
            "push_pull", "cascaded_hbridge", "npc_inverter",
            "buck", "boost", "buck_boost", "cuk", "sepic",
            "flyback", "forward", "dual_active_bridge",
        }
        assert expected.issubset(set(CONVERTER_REGISTRY.keys()))

    @pytest.mark.parametrize("key", list(CONVERTER_REGISTRY.keys()))
    def test_converter_has_info(self, key):
        cls = CONVERTER_REGISTRY[key]
        info = cls.get_info()
        assert info.name
        assert info.category in ("AC-DC", "DC-DC", "DC-AC")
        assert info.description

    @pytest.mark.parametrize("key", list(CONVERTER_REGISTRY.keys()))
    def test_converter_has_schema(self, key):
        cls = CONVERTER_REGISTRY[key]
        schema = cls.get_param_schema()
        assert isinstance(schema, dict)
        assert len(schema) > 0


# ---------------------------------------------------------------------------
# Theme Tests
# ---------------------------------------------------------------------------

class TestThemes:
    def test_theme_registry_has_three_themes(self):
        assert len(THEME_REGISTRY) >= 3
        for name in ("oscilloscope", "dark", "light"):
            assert name in THEME_REGISTRY

    def test_backward_compat_themes_dict(self):
        assert isinstance(THEMES, dict)
        for key in THEMES:
            assert "paper_bgcolor" in THEMES[key]
            assert "font_color" in THEMES[key]

    def test_get_theme_returns_theme(self):
        theme = get_theme("oscilloscope")
        assert isinstance(theme, Theme)
        assert theme.name == "oscilloscope"

    def test_get_theme_default_fallback(self):
        theme = get_theme("nonexistent")
        assert isinstance(theme, Theme)

    def test_trace_colors(self):
        theme = get_theme("oscilloscope")
        c0 = get_trace_color(theme, 0)
        c1 = get_trace_color(theme, 1)
        assert isinstance(c0, str)
        assert isinstance(c1, str)

    def test_trace_color_wraps(self):
        theme = get_theme("oscilloscope")
        n = len(theme.colors.trace_colors)
        assert get_trace_color(theme, 0) == get_trace_color(theme, n)
