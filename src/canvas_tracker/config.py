from __future__ import annotations

import json
import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "canvas_tracker"
CONFIG_FILE = CONFIG_DIR / "config.json"


def get_config() -> dict:
    """Read config from environment variable or saved config file."""
    config: dict[str, str] = {}

    if os.environ.get("CANVAS_ICAL_URL"):
        config["ical_url"] = os.environ["CANVAS_ICAL_URL"]

    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            saved = json.load(f)
        for key, value in saved.items():
            config.setdefault(key, value)

    return config


def save_config(ical_url: str) -> None:
    """Save the iCal URL to disk with restricted permissions."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump({"ical_url": ical_url}, f, indent=2)
    os.chmod(CONFIG_FILE, 0o600)  # owner read/write only — protects your URL