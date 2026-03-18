"""Tests for export module."""

from __future__ import annotations

import json

import numpy as np

from power_electronics.dashboard.export import (
    export_csv,
    export_figure_bytes,
    export_json,
    export_pdf_report,
)


def _sample_data():
    t = np.linspace(0, 0.1, 500)
    signals = {
        "Vout": 12.0 + 0.1 * np.sin(2 * np.pi * 1000 * t),
        "IL": 1.0 + 0.05 * np.sin(2 * np.pi * 1000 * t),
    }
    metrics = {"Vdc_avg": 12.0, "efficiency_%": 92.5, "ripple_%": 0.8}
    params = {"Vin": 48.0, "duty_cycle": 0.25}
    return t, signals, metrics, params


class TestExportCSV:
    def test_csv_contains_metrics(self):
        t, signals, metrics, _ = _sample_data()
        csv_text = export_csv(t, signals, metrics, "buck")
        assert "buck" in csv_text
        assert "Vdc_avg" in csv_text
        assert "efficiency_%" in csv_text

    def test_csv_contains_waveforms(self):
        t, signals, metrics, _ = _sample_data()
        csv_text = export_csv(t, signals, metrics, "buck")
        assert "time_s" in csv_text
        assert "Vout" in csv_text
        lines = csv_text.strip().split("\n")
        assert len(lines) > 100  # header + data rows

    def test_csv_nonempty(self):
        t, signals, metrics, _ = _sample_data()
        csv_text = export_csv(t, signals, metrics, "test")
        assert len(csv_text) > 0


class TestExportJSON:
    def test_json_valid(self):
        t, signals, metrics, params = _sample_data()
        json_str = export_json(t, signals, metrics, "buck", params)
        data = json.loads(json_str)
        assert "metadata" in data
        assert "metrics" in data
        assert "waveforms" in data
        assert "parameters" in data

    def test_json_downsample(self):
        t = np.linspace(0, 1, 10000)
        signals = {"V": np.sin(t)}
        metrics = {"a": 1.0}
        json_str = export_json(t, signals, metrics, "test", {})
        data = json.loads(json_str)
        # Should be downsampled to ~2000
        assert len(data["waveforms"]["time_s"]) <= 2001

    def test_json_metrics_rounded(self):
        t, signals, metrics, params = _sample_data()
        json_str = export_json(t, signals, metrics, "buck", params)
        data = json.loads(json_str)
        for v in data["metrics"].values():
            assert isinstance(v, (int, float))


class TestExportFigure:
    def test_png_bytes(self):
        t, signals, _, _ = _sample_data()
        data = export_figure_bytes(t, signals, fmt="png")
        assert isinstance(data, bytes)
        assert len(data) > 100
        assert data[:4] == b"\x89PNG"

    def test_svg_bytes(self):
        t, signals, _, _ = _sample_data()
        data = export_figure_bytes(t, signals, fmt="svg")
        assert isinstance(data, bytes)
        assert b"<svg" in data

    def test_selected_signals(self):
        t, signals, _, _ = _sample_data()
        data = export_figure_bytes(t, signals, selected_signals=["Vout"])
        assert isinstance(data, bytes)
        assert len(data) > 100


class TestExportPDF:
    def test_pdf_bytes(self):
        t, signals, metrics, params = _sample_data()
        data = export_pdf_report(t, signals, metrics, "buck", params)
        assert isinstance(data, bytes)
        assert len(data) > 100
        assert data[:4] == b"%PDF"

    def test_pdf_with_selected_signals(self):
        t, signals, metrics, params = _sample_data()
        data = export_pdf_report(t, signals, metrics, "buck", params, ["Vout"])
        assert isinstance(data, bytes)
        assert data[:4] == b"%PDF"
