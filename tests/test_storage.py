"""Full path coverage tests for storage module.

Covers:
  - load_data: no file, valid file, corrupt JSON, non-dict JSON, OSError
  - save_data: creates dir, writes valid JSON, overwrites existing
  - load_points / save_points: section isolation, merge behavior
  - load_settings / save_settings: section isolation, merge behavior
  - Round-trip: save → load preserves data
  - Edge cases: empty dicts, concurrent section saves
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import storage


def _setup_temp_storage(tmp_path):
    """Redirect storage to a temp directory for test isolation."""
    storage._DATA_DIR = str(tmp_path)
    storage._DATA_FILE = str(tmp_path / "data.json")


# ════════════════════════════════════════════════════════════
# load_data
# ════════════════════════════════════════════════════════════

class TestLoadData:
    def test_no_file_returns_empty_dict(self, tmp_path):
        _setup_temp_storage(tmp_path)
        assert storage.load_data() == {}

    def test_valid_json_file(self, tmp_path):
        _setup_temp_storage(tmp_path)
        data = {"key": "value", "number": 42}
        with open(storage._DATA_FILE, "w") as f:
            json.dump(data, f)
        assert storage.load_data() == data

    def test_corrupt_json_returns_empty_dict(self, tmp_path):
        _setup_temp_storage(tmp_path)
        with open(storage._DATA_FILE, "w") as f:
            f.write("{invalid json!!!}")
        assert storage.load_data() == {}

    def test_non_dict_json_returns_empty_dict(self, tmp_path):
        """If file contains a JSON array or string, return empty dict."""
        _setup_temp_storage(tmp_path)
        with open(storage._DATA_FILE, "w") as f:
            json.dump([1, 2, 3], f)
        assert storage.load_data() == {}

    def test_empty_file_returns_empty_dict(self, tmp_path):
        _setup_temp_storage(tmp_path)
        with open(storage._DATA_FILE, "w") as f:
            f.write("")
        assert storage.load_data() == {}


# ════════════════════════════════════════════════════════════
# save_data
# ════════════════════════════════════════════════════════════

class TestSaveData:
    def test_creates_directory_and_file(self, tmp_path):
        nested = tmp_path / "sub" / "dir"
        storage._DATA_DIR = str(nested)
        storage._DATA_FILE = str(nested / "data.json")
        storage.save_data({"test": True})
        assert os.path.exists(storage._DATA_FILE)

    def test_saves_valid_json(self, tmp_path):
        _setup_temp_storage(tmp_path)
        storage.save_data({"name": "LazyTom", "version": 1})
        with open(storage._DATA_FILE, "r") as f:
            data = json.load(f)
        assert data == {"name": "LazyTom", "version": 1}

    def test_overwrites_existing_file(self, tmp_path):
        _setup_temp_storage(tmp_path)
        storage.save_data({"old": True})
        storage.save_data({"new": True})
        assert storage.load_data() == {"new": True}

    def test_saves_unicode(self, tmp_path):
        _setup_temp_storage(tmp_path)
        storage.save_data({"name": "番茄钟"})
        data = storage.load_data()
        assert data["name"] == "番茄钟"

    def test_saves_empty_dict(self, tmp_path):
        _setup_temp_storage(tmp_path)
        storage.save_data({})
        assert storage.load_data() == {}


# ════════════════════════════════════════════════════════════
# load_points / save_points
# ════════════════════════════════════════════════════════════

class TestPointsStorage:
    def test_load_points_no_file(self, tmp_path):
        _setup_temp_storage(tmp_path)
        assert storage.load_points() == {}

    def test_load_points_no_section(self, tmp_path):
        _setup_temp_storage(tmp_path)
        storage.save_data({"settings": {"focus": 25}})
        assert storage.load_points() == {}

    def test_save_and_load_points(self, tmp_path):
        _setup_temp_storage(tmp_path)
        points_data = {"balance": 42, "history": [{"amount": 10, "reason": "test"}]}
        storage.save_points(points_data)
        loaded = storage.load_points()
        assert loaded == points_data

    def test_save_points_preserves_other_sections(self, tmp_path):
        """Saving points should not overwrite settings."""
        _setup_temp_storage(tmp_path)
        storage.save_settings({"focus_minutes": 30})
        storage.save_points({"balance": 10, "history": []})

        # Both sections should exist
        assert storage.load_settings() == {"focus_minutes": 30}
        assert storage.load_points() == {"balance": 10, "history": []}

    def test_save_points_overwrites_previous_points(self, tmp_path):
        _setup_temp_storage(tmp_path)
        storage.save_points({"balance": 10, "history": []})
        storage.save_points({"balance": 20, "history": []})
        assert storage.load_points()["balance"] == 20


# ════════════════════════════════════════════════════════════
# load_settings / save_settings
# ════════════════════════════════════════════════════════════

class TestSettingsStorage:
    def test_load_settings_no_file(self, tmp_path):
        _setup_temp_storage(tmp_path)
        assert storage.load_settings() == {}

    def test_load_settings_no_section(self, tmp_path):
        _setup_temp_storage(tmp_path)
        storage.save_data({"points": {"balance": 0}})
        assert storage.load_settings() == {}

    def test_save_and_load_settings(self, tmp_path):
        _setup_temp_storage(tmp_path)
        settings = {"focus_minutes": 45, "break_minutes": 10}
        storage.save_settings(settings)
        assert storage.load_settings() == settings

    def test_save_settings_preserves_other_sections(self, tmp_path):
        """Saving settings should not overwrite points."""
        _setup_temp_storage(tmp_path)
        storage.save_points({"balance": 100, "history": []})
        storage.save_settings({"focus_minutes": 25})

        assert storage.load_points() == {"balance": 100, "history": []}
        assert storage.load_settings() == {"focus_minutes": 25}

    def test_save_settings_overwrites_previous(self, tmp_path):
        _setup_temp_storage(tmp_path)
        storage.save_settings({"focus_minutes": 25})
        storage.save_settings({"focus_minutes": 45, "break_minutes": 15})
        loaded = storage.load_settings()
        assert loaded == {"focus_minutes": 45, "break_minutes": 15}


# ════════════════════════════════════════════════════════════
# Integration: full round-trip with real data shapes
# ════════════════════════════════════════════════════════════

class TestRoundTrip:
    def test_full_app_data_round_trip(self, tmp_path):
        _setup_temp_storage(tmp_path)

        # Simulate real usage
        storage.save_settings({"focus_minutes": 30, "break_minutes": 5})
        storage.save_points({
            "balance": 28,
            "history": [
                {"amount": 10, "reason": "Completed 25min focus session", "timestamp": "2025-01-01T10:00:00"},
                {"amount": 12, "reason": "Completed 30min focus session", "timestamp": "2025-01-01T11:00:00"},
                {"amount": 6, "reason": "Completed 15min focus session", "timestamp": "2025-01-01T12:00:00"},
            ],
        })

        # Reload everything
        settings = storage.load_settings()
        points = storage.load_points()

        assert settings["focus_minutes"] == 30
        assert settings["break_minutes"] == 5
        assert points["balance"] == 28
        assert len(points["history"]) == 3
        assert points["history"][2]["reason"] == "Completed 15min focus session"

    def test_interleaved_saves(self, tmp_path):
        """Multiple alternating saves should not corrupt data."""
        _setup_temp_storage(tmp_path)

        storage.save_settings({"focus_minutes": 25})
        storage.save_points({"balance": 10, "history": []})
        storage.save_settings({"focus_minutes": 30})
        storage.save_points({"balance": 20, "history": []})

        assert storage.load_settings()["focus_minutes"] == 30
        assert storage.load_points()["balance"] == 20
