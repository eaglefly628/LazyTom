"""Full path coverage tests for PomodoroTimer.

Tests every method, every branch, every state transition, and every edge case.

State machine transitions tested:
  IDLE -> RUNNING (start)
  RUNNING -> PAUSED (pause)
  PAUSED -> RUNNING (start/resume)
  RUNNING -> COMPLETED (tick to zero)
  COMPLETED -> RUNNING (start restarts)
  COMPLETED -> IDLE (reset)
  PAUSED -> IDLE (reset)
  RUNNING -> IDLE (reset)
  IDLE -> IDLE (reset, no-op safe)

Edge cases:
  - tick() in non-RUNNING states (no-op)
  - start() when already RUNNING (no-op)
  - pause() when not RUNNING (no-op)
  - set_duration() in non-IDLE states (rejected)
  - Zero duration timer
  - on_tick / on_complete callbacks (with and without)
  - progress boundary values (0.0, 0.5, 1.0)
  - formatted_time at various values
  - duration_minutes property
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from timer_engine import PomodoroTimer, TimerStatus


# ════════════════════════════════════════════════════════════
# Initial state
# ════════════════════════════════════════════════════════════

class TestInitialState:
    def test_default_duration(self):
        timer = PomodoroTimer()
        assert timer.total_seconds == 25 * 60
        assert timer.remaining_seconds == 25 * 60
        assert timer.status == TimerStatus.IDLE

    def test_custom_duration(self):
        timer = PomodoroTimer(duration_minutes=45)
        assert timer.total_seconds == 2700
        assert timer.remaining_seconds == 2700

    def test_callbacks_initially_none(self):
        timer = PomodoroTimer()
        assert timer.on_complete is None
        assert timer.on_tick is None


# ════════════════════════════════════════════════════════════
# formatted_time property
# ════════════════════════════════════════════════════════════

class TestFormattedTime:
    def test_full_25_minutes(self):
        timer = PomodoroTimer(duration_minutes=25)
        assert timer.formatted_time == "25:00"

    def test_after_one_tick(self):
        timer = PomodoroTimer(duration_minutes=25)
        timer.start()
        timer.tick()
        assert timer.formatted_time == "24:59"

    def test_one_minute_remaining(self):
        timer = PomodoroTimer(duration_minutes=1)
        assert timer.formatted_time == "01:00"

    def test_zero_remaining(self):
        timer = PomodoroTimer(duration_minutes=1)
        timer.start()
        for _ in range(60):
            timer.tick()
        assert timer.formatted_time == "00:00"

    def test_single_digit_seconds(self):
        timer = PomodoroTimer(duration_minutes=1)
        timer.start()
        for _ in range(55):
            timer.tick()
        assert timer.formatted_time == "00:05"

    def test_60_minutes(self):
        timer = PomodoroTimer(duration_minutes=60)
        assert timer.formatted_time == "60:00"


# ════════════════════════════════════════════════════════════
# progress property
# ════════════════════════════════════════════════════════════

class TestProgress:
    def test_full_progress(self):
        timer = PomodoroTimer(duration_minutes=1)
        assert timer.progress == 1.0

    def test_half_progress(self):
        timer = PomodoroTimer(duration_minutes=1)
        timer.start()
        for _ in range(30):
            timer.tick()
        assert abs(timer.progress - 0.5) < 0.02

    def test_zero_progress_at_completion(self):
        timer = PomodoroTimer(duration_minutes=1)
        timer.start()
        for _ in range(60):
            timer.tick()
        assert timer.progress == 0.0

    def test_zero_total_seconds(self):
        """Edge case: total_seconds == 0 should return 0.0, not divide-by-zero."""
        timer = PomodoroTimer(duration_minutes=0)
        assert timer.progress == 0.0


# ════════════════════════════════════════════════════════════
# smooth_progress property
# ════════════════════════════════════════════════════════════

class TestSmoothProgress:
    def test_idle_equals_progress(self):
        timer = PomodoroTimer(duration_minutes=1)
        assert timer.smooth_progress == timer.progress == 1.0

    def test_completed_equals_progress(self):
        timer = PomodoroTimer(duration_minutes=1)
        timer.start()
        for _ in range(60):
            timer.tick()
        assert timer.smooth_progress == 0.0

    def test_paused_equals_progress(self):
        timer = PomodoroTimer(duration_minutes=1)
        timer.start()
        timer.tick()
        timer.pause()
        assert timer.smooth_progress == timer.progress

    def test_running_uses_realtime(self):
        import timer_engine
        captured = [0.0]
        original_clock = timer_engine._clock
        timer_engine._clock = lambda: captured[0]
        try:
            timer = PomodoroTimer(duration_minutes=1)
            captured[0] = 100.0
            timer.start()
            captured[0] = 100.5  # 0.5 seconds elapsed
            sp = timer.smooth_progress
            assert 0.99 < sp < 1.0  # slightly less than 1.0
        finally:
            timer_engine._clock = original_clock

    def test_zero_total(self):
        timer = PomodoroTimer(duration_minutes=0)
        assert timer.smooth_progress == 0.0


# ════════════════════════════════════════════════════════════
# set_duration_seconds
# ════════════════════════════════════════════════════════════

class TestSetDurationSeconds:
    def test_set_10_seconds(self):
        timer = PomodoroTimer(duration_minutes=25)
        timer.set_duration_seconds(10)
        assert timer.total_seconds == 10
        assert timer.remaining_seconds == 10

    def test_rejected_when_running(self):
        timer = PomodoroTimer(duration_minutes=25)
        timer.start()
        timer.set_duration_seconds(10)
        assert timer.total_seconds == 1500

    def test_formatted_time_shows_seconds(self):
        timer = PomodoroTimer(duration_minutes=1)
        timer.set_duration_seconds(10)
        assert timer.formatted_time == "00:10"


# ════════════════════════════════════════════════════════════
# duration_minutes property
# ════════════════════════════════════════════════════════════

class TestDurationMinutes:
    def test_default(self):
        timer = PomodoroTimer(duration_minutes=25)
        assert timer.duration_minutes == 25

    def test_after_set_duration(self):
        timer = PomodoroTimer(duration_minutes=25)
        timer.set_duration(45)
        assert timer.duration_minutes == 45

    def test_zero(self):
        timer = PomodoroTimer(duration_minutes=0)
        assert timer.duration_minutes == 0


# ════════════════════════════════════════════════════════════
# set_duration()
# ════════════════════════════════════════════════════════════

class TestSetDuration:
    def test_set_when_idle(self):
        timer = PomodoroTimer(duration_minutes=25)
        timer.set_duration(45)
        assert timer.total_seconds == 2700
        assert timer.remaining_seconds == 2700

    def test_rejected_when_running(self):
        timer = PomodoroTimer(duration_minutes=25)
        timer.start()
        timer.set_duration(15)
        assert timer.total_seconds == 1500  # unchanged

    def test_rejected_when_paused(self):
        timer = PomodoroTimer(duration_minutes=25)
        timer.start()
        timer.pause()
        timer.set_duration(10)
        assert timer.total_seconds == 1500  # unchanged

    def test_rejected_when_completed(self):
        timer = PomodoroTimer(duration_minutes=1)
        timer.start()
        for _ in range(60):
            timer.tick()
        timer.set_duration(10)
        assert timer.total_seconds == 60  # unchanged

    def test_set_to_zero(self):
        timer = PomodoroTimer(duration_minutes=25)
        timer.set_duration(0)
        assert timer.total_seconds == 0
        assert timer.remaining_seconds == 0


# ════════════════════════════════════════════════════════════
# adjust_duration()
# ════════════════════════════════════════════════════════════

class TestAdjustDuration:
    def test_increase_above_5_steps_by_5(self):
        timer = PomodoroTimer(duration_minutes=25)
        timer.adjust_duration(5)
        assert timer.duration_minutes == 30

    def test_decrease_above_5_steps_by_5(self):
        timer = PomodoroTimer(duration_minutes=25)
        timer.adjust_duration(-5)
        assert timer.duration_minutes == 20

    def test_increase_below_5_steps_by_1(self):
        timer = PomodoroTimer(duration_minutes=3)
        timer.adjust_duration(1)
        assert timer.duration_minutes == 4

    def test_decrease_at_5_steps_by_1(self):
        timer = PomodoroTimer(duration_minutes=5)
        timer.adjust_duration(-1)
        assert timer.duration_minutes == 4

    def test_decrease_below_5_steps_by_1(self):
        timer = PomodoroTimer(duration_minutes=3)
        timer.adjust_duration(-1)
        assert timer.duration_minutes == 2

    def test_decrease_above_5_snaps_to_5(self):
        """Going down from 10 by -5 should land at 5, not below."""
        timer = PomodoroTimer(duration_minutes=10)
        timer.adjust_duration(-5)
        assert timer.duration_minutes == 5

    def test_decrease_from_7_snaps_to_5(self):
        timer = PomodoroTimer(duration_minutes=7)
        timer.adjust_duration(-5)
        assert timer.duration_minutes == 5

    def test_full_progression_down(self):
        """25 → 20 → 15 → 10 → 5 → 4 → 3 → 2 → 1"""
        timer = PomodoroTimer(duration_minutes=25)
        expected = [20, 15, 10, 5, 4, 3, 2, 1, 1]
        for exp in expected:
            timer.adjust_duration(-1)
            assert timer.duration_minutes == exp, f"Expected {exp}, got {timer.duration_minutes}"

    def test_full_progression_up(self):
        """1 → 2 → 3 → 4 → 5 → 10 → 15"""
        timer = PomodoroTimer(duration_minutes=1)
        expected = [2, 3, 4, 5, 10, 15]
        for exp in expected:
            timer.adjust_duration(1)
            assert timer.duration_minutes == exp, f"Expected {exp}, got {timer.duration_minutes}"

    def test_cannot_go_below_1(self):
        timer = PomodoroTimer(duration_minutes=1)
        timer.adjust_duration(-1)
        assert timer.duration_minutes == 1

    def test_rejected_when_running(self):
        timer = PomodoroTimer(duration_minutes=25)
        timer.start()
        timer.adjust_duration(5)
        assert timer.duration_minutes == 25

    def test_rejected_when_paused(self):
        timer = PomodoroTimer(duration_minutes=25)
        timer.start()
        timer.pause()
        timer.adjust_duration(5)
        assert timer.duration_minutes == 25

    def test_remaining_seconds_updated(self):
        timer = PomodoroTimer(duration_minutes=25)
        timer.adjust_duration(5)
        assert timer.remaining_seconds == 30 * 60


# ════════════════════════════════════════════════════════════
# State transitions: start()
# ════════════════════════════════════════════════════════════

class TestStart:
    def test_idle_to_running(self):
        timer = PomodoroTimer(duration_minutes=25)
        timer.start()
        assert timer.status == TimerStatus.RUNNING
        assert timer.remaining_seconds == 1500

    def test_start_resets_remaining_from_idle(self):
        """start() from IDLE always sets remaining = total."""
        timer = PomodoroTimer(duration_minutes=25)
        timer.remaining_seconds = 500  # manually tamper
        timer.start()
        assert timer.remaining_seconds == 1500  # reset to total

    def test_paused_to_running(self):
        timer = PomodoroTimer(duration_minutes=25)
        timer.start()
        timer.tick()
        timer.tick()
        timer.pause()
        remaining_before = timer.remaining_seconds
        timer.start()  # resume
        assert timer.status == TimerStatus.RUNNING
        assert timer.remaining_seconds == remaining_before  # preserved

    def test_completed_to_running(self):
        """start() from COMPLETED restarts the timer."""
        timer = PomodoroTimer(duration_minutes=1)
        timer.start()
        for _ in range(60):
            timer.tick()
        assert timer.status == TimerStatus.COMPLETED

        timer.start()
        assert timer.status == TimerStatus.RUNNING
        assert timer.remaining_seconds == 60  # reset to full

    def test_start_when_already_running_is_noop(self):
        timer = PomodoroTimer(duration_minutes=25)
        timer.start()
        timer.tick()
        remaining = timer.remaining_seconds
        timer.start()  # no-op
        assert timer.status == TimerStatus.RUNNING
        assert timer.remaining_seconds == remaining  # not reset


# ════════════════════════════════════════════════════════════
# State transitions: pause()
# ════════════════════════════════════════════════════════════

class TestPause:
    def test_running_to_paused(self):
        timer = PomodoroTimer(duration_minutes=25)
        timer.start()
        timer.pause()
        assert timer.status == TimerStatus.PAUSED

    def test_pause_when_idle_is_noop(self):
        timer = PomodoroTimer(duration_minutes=25)
        timer.pause()
        assert timer.status == TimerStatus.IDLE

    def test_pause_when_paused_is_noop(self):
        timer = PomodoroTimer(duration_minutes=25)
        timer.start()
        timer.pause()
        timer.pause()
        assert timer.status == TimerStatus.PAUSED

    def test_pause_when_completed_is_noop(self):
        timer = PomodoroTimer(duration_minutes=1)
        timer.start()
        for _ in range(60):
            timer.tick()
        timer.pause()
        assert timer.status == TimerStatus.COMPLETED


# ════════════════════════════════════════════════════════════
# State transitions: reset()
# ════════════════════════════════════════════════════════════

class TestReset:
    def test_reset_from_running(self):
        timer = PomodoroTimer(duration_minutes=25)
        timer.start()
        for _ in range(10):
            timer.tick()
        timer.reset()
        assert timer.status == TimerStatus.IDLE
        assert timer.remaining_seconds == 1500

    def test_reset_from_paused(self):
        timer = PomodoroTimer(duration_minutes=25)
        timer.start()
        timer.tick()
        timer.pause()
        timer.reset()
        assert timer.status == TimerStatus.IDLE
        assert timer.remaining_seconds == 1500

    def test_reset_from_completed(self):
        timer = PomodoroTimer(duration_minutes=1)
        timer.start()
        for _ in range(60):
            timer.tick()
        timer.reset()
        assert timer.status == TimerStatus.IDLE
        assert timer.remaining_seconds == 60

    def test_reset_from_idle(self):
        """Reset when already idle — should be safe no-op."""
        timer = PomodoroTimer(duration_minutes=25)
        timer.reset()
        assert timer.status == TimerStatus.IDLE
        assert timer.remaining_seconds == 1500


# ════════════════════════════════════════════════════════════
# tick()
# ════════════════════════════════════════════════════════════

class TestTick:
    def test_tick_decrements_by_one(self):
        timer = PomodoroTimer(duration_minutes=1)
        timer.start()
        timer.tick()
        assert timer.remaining_seconds == 59

    def test_tick_when_idle_is_noop(self):
        timer = PomodoroTimer(duration_minutes=25)
        timer.tick()
        assert timer.remaining_seconds == 1500

    def test_tick_when_paused_is_noop(self):
        timer = PomodoroTimer(duration_minutes=25)
        timer.start()
        timer.tick()
        timer.pause()
        remaining = timer.remaining_seconds
        timer.tick()
        assert timer.remaining_seconds == remaining

    def test_tick_when_completed_is_noop(self):
        timer = PomodoroTimer(duration_minutes=1)
        timer.start()
        for _ in range(60):
            timer.tick()
        timer.tick()  # extra tick after completion
        assert timer.remaining_seconds == 0
        assert timer.status == TimerStatus.COMPLETED

    def test_tick_triggers_completion(self):
        timer = PomodoroTimer(duration_minutes=1)
        timer.start()
        for _ in range(59):
            timer.tick()
        assert timer.status == TimerStatus.RUNNING
        timer.tick()  # the 60th tick
        assert timer.status == TimerStatus.COMPLETED
        assert timer.remaining_seconds == 0

    def test_tick_calls_on_tick_callback(self):
        timer = PomodoroTimer(duration_minutes=1)
        tick_count = 0

        def on_tick():
            nonlocal tick_count
            tick_count += 1

        timer.on_tick = on_tick
        timer.start()
        timer.tick()
        timer.tick()
        timer.tick()
        assert tick_count == 3

    def test_tick_calls_on_complete_callback(self):
        timer = PomodoroTimer(duration_minutes=1)
        completed = False

        def on_complete():
            nonlocal completed
            completed = True

        timer.on_complete = on_complete
        timer.start()
        for _ in range(60):
            timer.tick()
        assert completed is True

    def test_tick_without_on_complete_callback(self):
        """Completion should work even without a callback set."""
        timer = PomodoroTimer(duration_minutes=1)
        timer.start()
        for _ in range(60):
            timer.tick()
        assert timer.status == TimerStatus.COMPLETED

    def test_tick_without_on_tick_callback(self):
        """Tick should work even without on_tick set."""
        timer = PomodoroTimer(duration_minutes=1)
        timer.start()
        timer.tick()
        assert timer.remaining_seconds == 59

    def test_on_tick_called_on_completion_tick(self):
        """Both on_tick and on_complete should fire on the final tick."""
        timer = PomodoroTimer(duration_minutes=1)
        events = []

        timer.on_tick = lambda: events.append("tick")
        timer.on_complete = lambda: events.append("complete")

        timer.start()
        for _ in range(60):
            timer.tick()

        # on_tick fires every tick (60 times), on_complete fires once
        assert events.count("tick") == 60
        assert events.count("complete") == 1
        # on_tick fires before on_complete on the final tick
        assert events[-2] == "tick"
        assert events[-1] == "complete"


# ════════════════════════════════════════════════════════════
# Full lifecycle scenarios
# ════════════════════════════════════════════════════════════

class TestFullLifecycle:
    def test_start_pause_resume_complete(self):
        """Full flow: start → pause → resume → complete."""
        timer = PomodoroTimer(duration_minutes=1)
        completed = False
        timer.on_complete = lambda: None.__class__  # dummy
        completed_flag = []
        timer.on_complete = lambda: completed_flag.append(True)

        timer.start()
        assert timer.status == TimerStatus.RUNNING

        for _ in range(20):
            timer.tick()
        assert timer.remaining_seconds == 40

        timer.pause()
        assert timer.status == TimerStatus.PAUSED

        timer.start()  # resume
        assert timer.status == TimerStatus.RUNNING

        for _ in range(40):
            timer.tick()
        assert timer.status == TimerStatus.COMPLETED
        assert len(completed_flag) == 1

    def test_complete_then_restart(self):
        """After completion, start() should restart from full duration."""
        timer = PomodoroTimer(duration_minutes=1)
        timer.start()
        for _ in range(60):
            timer.tick()
        assert timer.status == TimerStatus.COMPLETED

        timer.start()
        assert timer.status == TimerStatus.RUNNING
        assert timer.remaining_seconds == 60
        assert timer.progress == 1.0

    def test_multiple_resets(self):
        timer = PomodoroTimer(duration_minutes=1)
        timer.start()
        timer.tick()
        timer.reset()
        timer.reset()
        timer.reset()
        assert timer.status == TimerStatus.IDLE
        assert timer.remaining_seconds == 60

    def test_change_duration_between_sessions(self):
        """Complete a session, reset, change duration, start new session."""
        timer = PomodoroTimer(duration_minutes=1)
        timer.start()
        for _ in range(60):
            timer.tick()
        timer.reset()
        timer.set_duration(2)
        timer.start()
        assert timer.remaining_seconds == 120
