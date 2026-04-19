"""Pomodoro timer core logic — pure Python, no UI dependency."""

import time
from enum import Enum

_clock = time.monotonic


class TimerStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"


class PomodoroTimer:
    def __init__(self, duration_minutes: int = 25):
        self.total_seconds = duration_minutes * 60
        self.remaining_seconds = self.total_seconds
        self.status = TimerStatus.IDLE
        self.on_complete = None
        self.on_tick = None
        self._run_start_time = None
        self._run_start_remaining = None

    @property
    def formatted_time(self) -> str:
        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    @property
    def progress(self) -> float:
        if self.total_seconds == 0:
            return 0.0
        return self.remaining_seconds / self.total_seconds

    @property
    def smooth_progress(self) -> float:
        """Time-based smooth progress for ring animation (updates every frame)."""
        if self.status != TimerStatus.RUNNING or self._run_start_time is None:
            return self.progress
        elapsed = _clock() - self._run_start_time
        smooth_remaining = max(0.0, self._run_start_remaining - elapsed)
        if self.total_seconds == 0:
            return 0.0
        return smooth_remaining / self.total_seconds

    def set_duration(self, minutes: int):
        if self.status == TimerStatus.IDLE:
            self.total_seconds = max(0, minutes * 60)
            self.remaining_seconds = self.total_seconds

    def set_duration_seconds(self, seconds: int):
        if self.status == TimerStatus.IDLE:
            self.total_seconds = max(0, seconds)
            self.remaining_seconds = self.total_seconds

    def adjust_duration(self, delta_minutes: int):
        """Adjust duration by delta minutes. Only when idle. Minimum 1 min."""
        if self.status == TimerStatus.IDLE:
            new_minutes = max(1, self.duration_minutes + delta_minutes)
            self.set_duration(new_minutes)

    def start(self):
        if self.status in (TimerStatus.IDLE, TimerStatus.COMPLETED):
            self.remaining_seconds = self.total_seconds
            self.status = TimerStatus.RUNNING
            self._run_start_time = _clock()
            self._run_start_remaining = self.remaining_seconds
        elif self.status == TimerStatus.PAUSED:
            self.status = TimerStatus.RUNNING
            self._run_start_time = _clock()
            self._run_start_remaining = self.remaining_seconds

    def pause(self):
        if self.status == TimerStatus.RUNNING:
            self.status = TimerStatus.PAUSED
            self._run_start_time = None

    def reset(self):
        self.remaining_seconds = self.total_seconds
        self.status = TimerStatus.IDLE
        self._run_start_time = None
        self._run_start_remaining = None

    def tick(self):
        if self.status != TimerStatus.RUNNING:
            return

        self.remaining_seconds -= 1

        if self.on_tick:
            self.on_tick()

        if self.remaining_seconds <= 0:
            self.remaining_seconds = 0
            self.status = TimerStatus.COMPLETED
            self._run_start_time = None
            if self.on_complete:
                self.on_complete()

    @property
    def duration_minutes(self) -> int:
        return self.total_seconds // 60
