"""Full path coverage tests for PointsManager and PointTransaction.

Covers:
  - PointTransaction: creation, auto-timestamp, serialization, from_dict with/without timestamp
  - PointsManager: initial state, add_points, balance accumulation, history ordering
  - award_for_pomodoro: various durations, minimum 1 point, reason text
  - Serialization: to_dict / load_from_dict round-trip, empty data, missing keys
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from points_engine import PointsManager, PointTransaction, POINTS_PER_MINUTE


# ════════════════════════════════════════════════════════════
# PointTransaction
# ════════════════════════════════════════════════════════════

class TestPointTransaction:
    def test_creation_with_explicit_timestamp(self):
        txn = PointTransaction(10, "Test", "2025-01-01T12:00:00")
        assert txn.amount == 10
        assert txn.reason == "Test"
        assert txn.timestamp == "2025-01-01T12:00:00"

    def test_creation_with_auto_timestamp(self):
        """When no timestamp given, should auto-generate an ISO format string."""
        txn = PointTransaction(5, "Auto time")
        assert txn.amount == 5
        assert txn.reason == "Auto time"
        assert txn.timestamp is not None
        assert "T" in txn.timestamp  # ISO format contains 'T'

    def test_to_dict(self):
        txn = PointTransaction(10, "Session", "2025-06-15T09:30:00")
        data = txn.to_dict()
        assert data == {
            "amount": 10,
            "reason": "Session",
            "timestamp": "2025-06-15T09:30:00",
        }

    def test_from_dict_with_timestamp(self):
        data = {"amount": 7, "reason": "Bonus", "timestamp": "2025-03-01T08:00:00"}
        txn = PointTransaction.from_dict(data)
        assert txn.amount == 7
        assert txn.reason == "Bonus"
        assert txn.timestamp == "2025-03-01T08:00:00"

    def test_from_dict_without_timestamp(self):
        """If timestamp key is missing, should auto-generate."""
        data = {"amount": 3, "reason": "No time"}
        txn = PointTransaction.from_dict(data)
        assert txn.amount == 3
        assert txn.reason == "No time"
        assert txn.timestamp is not None  # auto-generated

    def test_round_trip(self):
        """to_dict → from_dict preserves all fields."""
        original = PointTransaction(42, "Round trip", "2025-12-25T00:00:00")
        restored = PointTransaction.from_dict(original.to_dict())
        assert restored.amount == original.amount
        assert restored.reason == original.reason
        assert restored.timestamp == original.timestamp


# ════════════════════════════════════════════════════════════
# PointsManager — basic operations
# ════════════════════════════════════════════════════════════

class TestPointsManagerBasic:
    def test_initial_state(self):
        pm = PointsManager()
        assert pm.balance == 0
        assert pm.history == []
        assert pm.get_history() == []

    def test_add_points_single(self):
        pm = PointsManager()
        pm.add_points(10, "First reward")
        assert pm.balance == 10
        assert len(pm.history) == 1
        assert pm.history[0].amount == 10
        assert pm.history[0].reason == "First reward"

    def test_add_points_accumulates(self):
        pm = PointsManager()
        pm.add_points(10, "A")
        pm.add_points(5, "B")
        pm.add_points(3, "C")
        assert pm.balance == 18

    def test_get_history_most_recent_first(self):
        pm = PointsManager()
        pm.add_points(10, "First")
        pm.add_points(5, "Second")
        pm.add_points(3, "Third")
        history = pm.get_history()
        assert len(history) == 3
        assert history[0].reason == "Third"
        assert history[1].reason == "Second"
        assert history[2].reason == "First"

    def test_get_history_returns_copy(self):
        """Modifying returned list should not affect internal state."""
        pm = PointsManager()
        pm.add_points(10, "Test")
        history = pm.get_history()
        history.clear()
        assert len(pm.get_history()) == 1  # internal list unchanged


# ════════════════════════════════════════════════════════════
# award_for_pomodoro — various durations
# ════════════════════════════════════════════════════════════

class TestAwardForPomodoro:
    def test_25_minutes(self):
        pm = PointsManager()
        pm.award_for_pomodoro(25)
        assert pm.balance == 10  # 25 * 0.4 = 10

    def test_15_minutes(self):
        pm = PointsManager()
        pm.award_for_pomodoro(15)
        assert pm.balance == 6  # 15 * 0.4 = 6

    def test_20_minutes(self):
        pm = PointsManager()
        pm.award_for_pomodoro(20)
        assert pm.balance == 8  # 20 * 0.4 = 8

    def test_30_minutes(self):
        pm = PointsManager()
        pm.award_for_pomodoro(30)
        assert pm.balance == 12  # 30 * 0.4 = 12

    def test_45_minutes(self):
        pm = PointsManager()
        pm.award_for_pomodoro(45)
        assert pm.balance == 18  # 45 * 0.4 = 18

    def test_60_minutes(self):
        pm = PointsManager()
        pm.award_for_pomodoro(60)
        assert pm.balance == 24  # 60 * 0.4 = 24

    def test_1_minute_minimum(self):
        """Minimum 1 point even for very short sessions."""
        pm = PointsManager()
        pm.award_for_pomodoro(1)
        assert pm.balance == 1  # max(1, round(1 * 0.4)) = max(1, 0) = 1

    def test_2_minutes(self):
        pm = PointsManager()
        pm.award_for_pomodoro(2)
        assert pm.balance == 1  # max(1, round(0.8)) = max(1, 1) = 1

    def test_reason_text_format(self):
        pm = PointsManager()
        pm.award_for_pomodoro(25)
        assert pm.get_history()[0].reason == "Completed 25min focus session"

    def test_multiple_sessions(self):
        pm = PointsManager()
        pm.award_for_pomodoro(25)
        pm.award_for_pomodoro(25)
        pm.award_for_pomodoro(15)
        assert pm.balance == 26  # 10 + 10 + 6
        assert len(pm.get_history()) == 3

    def test_points_per_minute_constant(self):
        assert POINTS_PER_MINUTE == 0.4


# ════════════════════════════════════════════════════════════
# Serialization — to_dict / load_from_dict
# ════════════════════════════════════════════════════════════

class TestSerialization:
    def test_to_dict_empty(self):
        pm = PointsManager()
        data = pm.to_dict()
        assert data == {"balance": 0, "history": []}

    def test_to_dict_with_data(self):
        pm = PointsManager()
        pm.add_points(10, "Test")
        data = pm.to_dict()
        assert data["balance"] == 10
        assert len(data["history"]) == 1
        assert data["history"][0]["amount"] == 10
        assert data["history"][0]["reason"] == "Test"
        assert "timestamp" in data["history"][0]

    def test_load_from_dict_full(self):
        data = {
            "balance": 25,
            "history": [
                {"amount": 10, "reason": "Session 1", "timestamp": "2025-01-01T10:00:00"},
                {"amount": 15, "reason": "Session 2", "timestamp": "2025-01-01T11:00:00"},
            ],
        }
        pm = PointsManager()
        pm.load_from_dict(data)
        assert pm.balance == 25
        assert len(pm.history) == 2
        assert pm.history[0].reason == "Session 1"
        assert pm.history[1].reason == "Session 2"

    def test_load_from_dict_empty(self):
        pm = PointsManager()
        pm.load_from_dict({})
        assert pm.balance == 0
        assert pm.history == []

    def test_load_from_dict_missing_balance(self):
        pm = PointsManager()
        pm.load_from_dict({"history": []})
        assert pm.balance == 0

    def test_load_from_dict_missing_history(self):
        pm = PointsManager()
        pm.load_from_dict({"balance": 50})
        assert pm.balance == 50
        assert pm.history == []

    def test_round_trip(self):
        """to_dict → load_from_dict preserves all data."""
        pm1 = PointsManager()
        pm1.add_points(10, "A")
        pm1.add_points(5, "B")
        pm1.award_for_pomodoro(25)

        data = pm1.to_dict()

        pm2 = PointsManager()
        pm2.load_from_dict(data)

        assert pm2.balance == pm1.balance
        assert len(pm2.history) == len(pm1.history)
        for t1, t2 in zip(pm1.history, pm2.history):
            assert t1.amount == t2.amount
            assert t1.reason == t2.reason
            assert t1.timestamp == t2.timestamp

    def test_load_overwrites_existing_state(self):
        """load_from_dict should replace, not merge with existing state."""
        pm = PointsManager()
        pm.add_points(100, "Old data")
        assert pm.balance == 100

        pm.load_from_dict({"balance": 5, "history": []})
        assert pm.balance == 5
        assert pm.history == []
