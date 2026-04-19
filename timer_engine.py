"""Pomodoro timer core logic — pure Python, no UI dependency."""

from enum import Enum


class TimerStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"


class PomodoroTimer:
    """A simple Pomodoro countdown timer.

    Usage:
        timer = PomodoroTimer(duration_minutes=25)
        timer.on_complete = lambda: print("Done!")
        timer.start()
        # Call timer.tick() every second from your UI loop
    """

    def __init__(self, duration_minutes: int = 25):
        self.total_seconds = duration_minutes * 60
        self.remaining_seconds = self.total_seconds
        self.status = TimerStatus.IDLE
        self.on_complete = None  # callback when timer finishes
        self.on_tick = None      # callback every second

    @property
    def formatted_time(self) -> str:
        """Return remaining time as 'mm:ss'."""
        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    @property
    def progress(self) -> float:
        """Return progress from 1.0 (full) to 0.0 (done)."""
        if self.total_seconds == 0:
            return 0.0
        return self.remaining_seconds / self.total_seconds

    def set_duration(self, minutes: int):
        """Change the timer duration. Only works when idle."""
        if self.status == TimerStatus.IDLE:
            self.total_seconds = max(0, minutes * 60)
            self.remaining_seconds = self.total_seconds

    def adjust_duration(self, delta_minutes: int):
        """Adjust duration by delta minutes. Only works when idle. Minimum 5 min."""
        if self.status == TimerStatus.IDLE:
            new_minutes = max(5, self.duration_minutes + delta_minutes)
            self.set_duration(new_minutes)

    def start(self):
        """Start or resume the timer."""
        if self.status in (TimerStatus.IDLE, TimerStatus.COMPLETED):
            self.remaining_seconds = self.total_seconds
            self.status = TimerStatus.RUNNING
        elif self.status == TimerStatus.PAUSED:
            self.status = TimerStatus.RUNNING

    def pause(self):
        """Pause the running timer."""
        if self.status == TimerStatus.RUNNING:
            self.status = TimerStatus.PAUSED

    def reset(self):
        """Reset timer back to idle with full duration."""
        self.remaining_seconds = self.total_seconds
        self.status = TimerStatus.IDLE

    def tick(self):
        """Call this every second. Decrements the timer and handles completion."""
        if self.status != TimerStatus.RUNNING:
            return

        self.remaining_seconds -= 1

        if self.on_tick:
            self.on_tick()

        if self.remaining_seconds <= 0:
            self.remaining_seconds = 0
            self.status = TimerStatus.COMPLETED
            if self.on_complete:
                self.on_complete()

    @property
    def duration_minutes(self) -> int:
        """Return the configured duration in minutes."""
        return self.total_seconds // 60
