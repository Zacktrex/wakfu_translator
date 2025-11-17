# wakfu_translator/settings.py
"""
Robust settings loader/saver.

- Uses resource_path to handle frozen app (PyInstaller).
- Keeps DEFAULT_SETTINGS from the original single-file app.
- If config file doesn't exist, creates it with defaults.
- If config file is invalid (empty/corrupted), backs it up and resets to defaults.
- When loading, merges user's settings with defaults (preserves new defaults).
"""

import json
import os
import sys
import tempfile
from shutil import move
from constants import (
    WINDOW_OPACITY_DEFAULT,
    DEFAULT_CHECK_INTERVAL,
    DEFAULT_CHECK_LAST_LINES,
    DEFAULT_TARGET_LANGUAGE
)

def resource_path(relative_path: str) -> str:
    """
    Resolve path to resource (works when frozen with PyInstaller).
    """
    if getattr(sys, "frozen", False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Keep same default settings as original
SETTINGS_FILE = resource_path("config.json")

DEFAULT_SETTINGS = {
    "chat_log": "",
    "transparency": WINDOW_OPACITY_DEFAULT,
    "check_interval": DEFAULT_CHECK_INTERVAL,
    "check_last_lines": DEFAULT_CHECK_LAST_LINES,
    "target_lang": DEFAULT_TARGET_LANGUAGE,
    "tracked_players": {},  # {player_name: language_code}
}


def _atomic_write(path: str, data: str) -> None:
    """
    Write file atomically (write to temp then replace).
    """
    dirpath = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(dir=dirpath, prefix=".tmp_", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
        # Use os.replace for atomic replace on most OSes
        os.replace(tmp, path)
    except Exception:
        # fallback: try move
        try:
            move(tmp, path)
        except Exception:
            # last resort: write directly
            with open(path, "w", encoding="utf-8") as f:
                f.write(data)


def load_settings() -> dict:
    """
    Load settings from SETTINGS_FILE.

    - If file missing: create it with defaults and return a copy.
    - If file invalid JSON: backup corrupted file and reset to defaults.
    - If file valid: merge missing default keys and return.
    """
    # ensure defaults are not modified by callers
    defaults = DEFAULT_SETTINGS.copy()

    if not os.path.exists(SETTINGS_FILE):
        try:
            _atomic_write(SETTINGS_FILE, json.dumps(defaults, indent=4))
        except Exception:
            pass
        return defaults.copy()

    # file exists -> read safely
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("Settings file does not contain a JSON object.")
        # merge: user's values override defaults; keep any unknown keys too
        merged = defaults.copy()
        merged.update(data)
        return merged
    except Exception as e:
        # backup corrupted file
        try:
            bak_path = SETTINGS_FILE + ".bak"
            if os.path.exists(bak_path):
                # don't overwrite an existing backup; add a numeric suffix
                i = 1
                while os.path.exists(bak_path + f".{i}"):
                    i += 1
                bak_path = bak_path + f".{i}"
            os.replace(SETTINGS_FILE, bak_path)
        except Exception:
            pass

        # write defaults back
        try:
            _atomic_write(SETTINGS_FILE, json.dumps(defaults, indent=4))
        except Exception:
            pass

        return defaults.copy()


def save_settings(settings: dict) -> None:
    """
    Save settings dict to SETTINGS_FILE atomically.
    """
    # make sure we don't accidentally lose default keys when saving partial dicts -
    # but we write the dict the caller gave us (caller likely has merged settings).
    try:
        _atomic_write(SETTINGS_FILE, json.dumps(settings, indent=4, ensure_ascii=False))
    except Exception:
        # fallback plain write
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)


def load_tracked_players() -> dict:
    """
    Load tracked players from config.json.
    Returns dict: {player_name: language_code}
    Example: {"PlayerOne": "fr", "PlayerTwo": "es"}
    """
    settings = load_settings()
    return settings.get("tracked_players", {})


def save_tracked_players(tracked_players: dict) -> None:
    """
    Save tracked players dict to config.json.
    """
    settings = load_settings()
    settings["tracked_players"] = tracked_players
    save_settings(settings)

