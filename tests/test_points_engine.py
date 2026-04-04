"""Tests for PointsManager — balance, transactions, serialization."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from points_engine import PointsManager, PointTransaction


def test_initial_state():
    pm = PointsManager()
    assert pm.balance == 0
    assert pm.get_history() == []


def test_add_points():
    pm = PointsManager()
    pm.add_points(10, "Test reward")
    assert pm.balance == 10
    assert len(pm.get_history()) == 1
    assert pm.get_history()[0].amount == 10
    assert pm.get_history()[0].reason == "Test reward"


def test_multiple_transactions():
    pm = PointsManager()
    pm.add_points(10, "First")
    pm.add_points(5, "Second")
    pm.add_points(3, "Third")
    assert pm.balance == 18
    assert len(pm.get_history()) == 3
    # Most recent first
    assert pm.get_history()[0].reason == "Third"


def test_award_for_pomodoro_25min():
    pm = PointsManager()
    pm.award_for_pomodoro(25)
    assert pm.balance == 10  # 25 * 0.4 = 10


def test_award_for_pomodoro_15min():
    pm = PointsManager()
    pm.award_for_pomodoro(15)
    assert pm.balance == 6  # 15 * 0.4 = 6


def test_award_for_pomodoro_minimum_1():
    pm = PointsManager()
    pm.award_for_pomodoro(1)
    assert pm.balance >= 1  # minimum 1 point


def test_serialization():
    pm = PointsManager()
    pm.add_points(10, "Session 1")
    pm.add_points(5, "Session 2")

    data = pm.to_dict()
    assert data["balance"] == 15
    assert len(data["history"]) == 2

    # Restore
    pm2 = PointsManager()
    pm2.load_from_dict(data)
    assert pm2.balance == 15
    assert len(pm2.get_history()) == 2
    assert pm2.get_history()[0].reason == "Session 2"


def test_transaction_serialization():
    txn = PointTransaction(10, "Test", "2025-01-01T12:00:00")
    data = txn.to_dict()
    assert data["amount"] == 10
    assert data["reason"] == "Test"
    assert data["timestamp"] == "2025-01-01T12:00:00"

    txn2 = PointTransaction.from_dict(data)
    assert txn2.amount == 10
    assert txn2.reason == "Test"
    assert txn2.timestamp == "2025-01-01T12:00:00"
