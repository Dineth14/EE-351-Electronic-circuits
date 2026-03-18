"""Dashboard application entry point."""

from __future__ import annotations

from pathlib import Path

import dash

from power_electronics.dashboard.callbacks import register_callbacks
from power_electronics.dashboard.layout import build_layout


def create_app() -> dash.Dash:
    """Create and configure Dash application instance."""
    project_root = Path(__file__).resolve().parents[2]
    assets_dir = str(project_root / "assets" / "dashboard")
    app = dash.Dash(__name__, suppress_callback_exceptions=True, assets_folder=assets_dir)
    app.title = "Power Electronics Simulator"
    app.layout = build_layout()
    register_callbacks(app)
    return app


def main() -> None:
    """Run dashboard development server."""
    app = create_app()
    app.run(debug=False, host="0.0.0.0", port=8050)


if __name__ == "__main__":
    main()
