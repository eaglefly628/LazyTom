"""Tests for PomodoroTimer — state transitions, tick behavior, formatting."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from timer_engine import PomodoroTimer, TimerStatus


def test_initial_state():
    timer = PomodoroTimer(duration_minutes=25)
    assert timer.status == TimerStatus.IDLE
    assert timer.remaining_seconds == 1500
    assert timer.total_seconds == 1500
    assert timer.formatted_time == "25:00"
    assert timer.progress == 1.0


def test_start():
    timer = PomodoroTimer(duration_minutes=25)
    timer.start()
    assert timer.status == TimerStatus.RUNNING
    assert timer.remaining_seconds == 1500


def test_tick_decrements():
    timer = PomodoroTimer(duration_minutes=1)
    timer.start()
    timer.tick()
    assert timer.remaining_seconds == 59
    assert timer.status == TimerStatus.RUNNING


def test_pause_and_resume():
    timer = PomodoroTimer(duration_minutes=25)
    timer.start()
    timer.tick()
    timer.pause()
    assert timer.status == TimerStatus.PAUSED
    remaining = timer.remaining_seconds

    # Tick should not decrement when paused
    timer.tick()
    assert timer.remaining_seconds == remaining

    # Resume
    timer.start()
    assert timer.status == TimerStatus.RUNNING
    timer.tick()
    assert timer.remaining_seconds == remaining - 1


def test_reset():
    timer = PomodoroTimer(duration_minutes=25)
    timer.start()
    for _ in range(10):
        timer.tick()
    timer.reset()
    assert timer.status == TimerStatus.IDLE
    assert timer.remaining_seconds == 1500


def test_completion():
    timer = PomodoroTimer(duration_minutes=1)
    timer.start()
    completed = False

    def on_complete():
        nonlocal completed
        completed = True

    timer.on_complete = on_complete

    # Tick 60 times to complete 1 minute
    for _ in range(60):
        timer.tick()

    assert timer.status == TimerStatus.COMPLETED
    assert timer.remaining_seconds == 0
    assert completed


def test_formatted_time():
    timer = PomodoroTimer(duration_minutes=25)
    assert timer.formatted_time == "25:00"

    timer.start()
    timer.tick()
    assert timer.formatted_time == "24:59"


def test_progress():
    timer = PomodoroTimer(duration_minutes=1)
    assert timer.progress == 1.0

    timer.start()
    for _ in range(30):
        timer.tick()
    assert abs(timer.progress - 0.5) < 0.02

    for _ in range(30):
        timer.tick()
    assert timer.progress == 0.0


def test_set_duration():
    timer = PomodoroTimer(duration_minutes=25)
    timer.set_duration(45)
    assert timer.total_seconds == 2700
    assert timer.remaining_seconds == 2700

    # Cannot change while running
    timer.start()
    timer.set_duration(15)
    assert timer.total_seconds == 2700  # unchanged


def test_set_duration_only_when_idle():
    timer = PomodoroTimer(duration_minutes=25)
    timer.start()
    timer.pause()
    timer.set_duration(10)
    assert timer.total_seconds == 1500  # unchanged, was paused not idle
