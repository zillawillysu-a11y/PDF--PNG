from __future__ import annotations

import sys
from pathlib import Path


def app_root() -> Path:
    """Return the app root for source runs and PyInstaller builds."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def icon_path(preferred: str = "icon.ico") -> Path | None:
    root = app_root()
    candidates = [
        root / "assets" / preferred,
        root / "assets" / "icon.png",
        root / "assets" / "icon.ico",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None
