# config_loader.py
# Reads settings.cfg into a plain dict of strings.

import warnings
from pathlib import Path

SETTINGS_FILE = Path(__file__).with_name("settings.cfg")

KNOWN_KEYS = (
    "service_interval_km",
    "warn_at_percent",
    "report_title",
    "history_file",
    "log_file",
    "mileage_unit",
)


def load_settings(path: str | Path | None = None) -> dict[str, str]:
    """Parse settings.cfg into a dict of known keys -> string values.

    Unknown keys are skipped with a warning, so a typo in the file is visible.
    """
    settings: dict[str, str] = {}
    with open(path or SETTINGS_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")   # split on the first = only
            key, value = key.strip(), value.strip()
            if key in KNOWN_KEYS:
                settings[key] = value
            else:
                warnings.warn(f"settings.cfg: unknown key {key!r} ignored", stacklevel=2)
    return settings


def get_int(settings: dict, key: str, fallback: int) -> int:
    """Return settings[key] as int, or fallback if absent or not a valid int."""
    try:
        return int(settings[key])
    except (KeyError, ValueError):
        return fallback


def get_setting(settings: dict, key: str, fallback: str = "") -> str:
    """Return settings[key], or fallback if the key is absent."""
    return settings.get(key, fallback)
