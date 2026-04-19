"""Local data persistence using JSON files."""

import json
import os

# Store data next to the app for simplicity
_DATA_DIR = os.path.join(os.path.expanduser("~"), ".lazytom")
_DATA_FILE = os.path.join(_DATA_DIR, "data.json")


def _ensure_dir():
    os.makedirs(_DATA_DIR, exist_ok=True)


def load_data() -> dict:
    """Load all app data from disk. Returns empty dict if no file or on error."""
    if not os.path.exists(_DATA_FILE):
        return {}
    try:
        with open(_DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def save_data(data: dict):
    """Save all app data to disk."""
    _ensure_dir()
    with open(_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_points() -> dict:
    """Load just the points section."""
    return load_data().get("points", {})


def save_points(points_data: dict):
    """Save just the points section (merges with existing data)."""
    data = load_data()
    data["points"] = points_data
    save_data(data)


def load_settings() -> dict:
    """Load settings section."""
    return load_data().get("settings", {})


def save_settings(settings_data: dict):
    """Save settings section (merges with existing data)."""
    data = load_data()
    data["settings"] = settings_data
    save_data(data)


def load_tasks() -> dict:
    """Load tasks section."""
    return load_data().get("tasks", {})


def save_tasks(tasks_data: dict):
    """Save tasks section (merges with existing data)."""
    data = load_data()
    data["tasks"] = tasks_data
    save_data(data)
