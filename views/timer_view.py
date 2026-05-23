"""Timer view — the main screen with countdown ring and controls.

New warm-linen design with session pills, date subtitle, streak chip.
"""

import asyncio
from datetime import datetime
import flet as ft
import theme
from theme import (
    BODY_FONT_SIZE, CAPTION_FONT_SIZE, PADDING_LG, PADDING_XL,
    PAGE_TITLE_SIZE, PADDING_MD,
)

from timer_engine import PomodoroTimer, TimerStatus
from points_engine import PointsManager
from components.countdown_ring import create_countdown_ring
from components.timer_controls import create_timer_controls
from components.points_badge import create_points_badge
from components.mood_picker import show_mood_picker
from mood_engine import MoodManager, MoodLevel
import storage

RENDER_FPS = 30
TEST_DURATION_SECONDS = 10
TOTAL_SESSIONS = 5


class TimerView:
    """Main timer screen with countdown ring, controls, and points badge."""

    def __init__(self, points_manager: PointsManager, mood_manager: MoodManager | None = None, on_points_changed=None):
        self.timer = PomodoroTimer(duration_minutes=25)
        self.points = points_manager
        self.mood = mood_manager or MoodManager()
        self.on_points_changed = on_points_changed
        self._is_ticking = False
        self._page: ft.Page | None = None
        self._container: ft.Container | None = None
        self._seconds_since_tick = 0.0
        self._current_task = None
        self._current_mood_log = None
        self._completed_sessions = 0
        self._current_session = 1

        settings = storage.load_settings()
        duration = settings.get("focus_minutes", 25)
        self.timer.set_duration(duration)

        self.timer.on_complete = self._on_timer_complete

    def _on_timer_complete(self):
        self._is_ticking = False
        duration_min = self.timer.total_seconds / 60.0
        self.points.award_for_pomodoro(max(1, round(duration_min)))
        storage.save_points(self.points.to_dict())
        self._completed_sessions += 1
        if self._current_session < TOTAL_SESSIONS:
            self._current_session += 1
        if self.on_points_changed:
            self.on_points_changed()
        self._rebuild()
        # Ask for mood-after, if a session was being tracked.
        if self._current_mood_log is not None and self._page is not None:
            log_entry = self._current_mood_log
            self._current_mood_log = None

            def _on_after(mood: MoodLevel):
                self.mood.complete_session(log_entry, mood, completed=True)
                self.mood.set_current_mood(mood)
                storage.save_mood(self.mood.to_dict())

            show_mood_picker(self._page, "How do you feel now?", _on_after)

    async def _render_loop(self):
        """Single loop: smooth ring animation at 30fps + 1-second ticks."""
        import time
        interval = 1.0 / RENDER_FPS
        last_tick_time = time.monotonic()
        while self._is_ticking and self.timer.status == TimerStatus.RUNNING:
            await asyncio.sleep(interval)
            if not self._is_ticking or self.timer.status != TimerStatus.RUNNING:
                break
            now = time.monotonic()
            if now - last_tick_time >= 1.0:
                last_tick_time += 1.0
                self.timer.tick()
            self._rebuild_ring()

    def _start_tick_loop(self):
        if self._is_ticking:
            return
        self._is_ticking = True
        if self._page:
            self._page.run_task(self._render_loop)

    def _stop_tick_loop(self):
        self._is_ticking = False

    def _begin_session(self, mood_before: MoodLevel | None):
        """Actually start the timer; log the session if we have a mood."""
        if mood_before is not None:
            self.mood.set_current_mood(mood_before)
            task_id = self._current_task.id if self._current_task else None
            self._current_mood_log = self.mood.start_session(task_id, mood_before)
            storage.save_mood(self.mood.to_dict())
        self.timer.start()
        self._start_tick_loop()
        self._rebuild()

    def _on_play_pause(self, e):
        if self.timer.status == TimerStatus.RUNNING:
            self.timer.pause()
            self._stop_tick_loop()
            self._rebuild()
            return
        if self.timer.status in (TimerStatus.IDLE, TimerStatus.COMPLETED, TimerStatus.PAUSED):
            from_paused = self.timer.status == TimerStatus.PAUSED
            if not from_paused and self._page is not None and not self.mood.has_mood_today():
                def _on_before(mood: MoodLevel):
                    self._begin_session(mood)
                show_mood_picker(self._page, "How are you feeling?", _on_before)
                return
            mood_before = self.mood.current_mood if (not from_paused and self.mood.has_mood_today()) else None
            self._begin_session(mood_before)

    def _on_cancel(self, e):
        self._stop_tick_loop()
        self.timer.reset()
        self._rebuild()

    def _adjust_duration(self, delta: int):
        if self.timer.status == TimerStatus.IDLE:
            self.timer.adjust_duration(delta)
            storage.save_settings({
                "focus_minutes": self.timer.duration_minutes,
                "break_minutes": storage.load_settings().get("break_minutes", 5),
            })
            self._rebuild()

    def _set_test_duration(self, e):
        """Set 10-second test duration."""
        if self.timer.status == TimerStatus.IDLE:
            self.timer.set_duration_seconds(TEST_DURATION_SECONDS)
            self._rebuild()

    def set_current_task(self, task):
        """Set the task to work on. Syncs task name and duration to timer."""
        self._current_task = task
        if self.timer.status == TimerStatus.IDLE:
            self.timer.set_duration(task.duration_minutes)
        self._rebuild()

    def _on_keyboard(self, e: ft.KeyboardEvent):
        if e.key == "Arrow Up":
            self._adjust_duration(5)
        elif e.key == "Arrow Down":
            self._adjust_duration(-5)

    def _rebuild(self):
        if self._page and self._container:
            self._container.content = self._build_content()
            self._page.update()

    def _rebuild_ring(self):
        """Fast path: only update the ring and time text for smooth animation."""
        if self._page and self._container:
            self._container.content = self._build_content()
            self._page.update()

    def _status_text(self) -> str:
        if self._current_task and self.timer.status in (TimerStatus.IDLE, TimerStatus.RUNNING, TimerStatus.PAUSED):
            return self._current_task.name
        status_map = {
            TimerStatus.IDLE: "Ready to focus",
            TimerStatus.RUNNING: "Focusing...",
            TimerStatus.PAUSED: "Paused",
            TimerStatus.COMPLETED: "Well done!",
        }
        return status_map.get(self.timer.status, "")

    def _build_session_pills(self) -> ft.Row:
        """Build 5 small session progress pills."""
        pills = []
        for i in range(1, TOTAL_SESSIONS + 1):
            if i <= self._completed_sessions:
                color = theme.MOSS
            elif i == self._current_session:
                color = theme.LEAF
            else:
                color = theme.DIVIDER_COLOR
            pill = ft.Container(
                width=22,
                height=6,
                border_radius=3,
                bgcolor=color,
            )
            pills.append(pill)
        return ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=6,
            controls=pills,
        )

    def _get_end_time_str(self) -> str | None:
        """Calculate the end time for running/idle timer."""
        if self.timer.status == TimerStatus.RUNNING:
            remaining = self.timer.remaining_seconds
        elif self.timer.status == TimerStatus.IDLE:
            remaining = self.timer.total_seconds
        else:
            return None
        now = datetime.now()
        end = now.replace(
            hour=(now.hour + (now.minute * 60 + now.second + remaining) // 3600) % 24,
            minute=((now.minute * 60 + now.second + remaining) % 3600) // 60,
            second=0,
        )
        return f"ends at {end.strftime('%I:%M %p').lstrip('0')}"

    def _build_content(self) -> ft.Column:
        is_running = self.timer.status == TimerStatus.RUNNING
        is_idle = self.timer.status == TimerStatus.IDLE
        is_paused = self.timer.status == TimerStatus.PAUSED

        # -- Header --
        now = datetime.now()
        date_str = now.strftime("%A, %B %d").upper()

        header = ft.Container(
            padding=ft.Padding.symmetric(horizontal=PADDING_LG),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(
                                "LazyTom",
                                size=PAGE_TITLE_SIZE,
                                color=theme.TEXT_PRIMARY,
                                weight=ft.FontWeight.W_700,
                            ),
                            ft.Text(
                                date_str,
                                size=CAPTION_FONT_SIZE,
                                color=theme.TEXT_SECONDARY,
                                weight=ft.FontWeight.W_600,
                            ),
                        ],
                    ),
                    create_points_badge(self.points.balance),
                ],
            ),
        )

        # -- Session pills --
        session_pills = self._build_session_pills()

        # -- Session caption --
        session_type = "Focus" if is_running or is_idle else ("Paused" if is_paused else "Done")
        session_caption = ft.Text(
            f"Session {self._current_session} of {TOTAL_SESSIONS} · {session_type}",
            size=CAPTION_FONT_SIZE,
            color=theme.TEXT_SECONDARY,
            weight=ft.FontWeight.W_600,
            text_align=ft.TextAlign.CENTER,
        )

        # -- Ring area --
        task_name = self._current_task.name if self._current_task else None
        end_time = self._get_end_time_str()

        ring = create_countdown_ring(
            self.timer.formatted_time,
            self.timer.smooth_progress,
            task_name=task_name,
            end_time_str=end_time,
        )

        can_adjust = is_idle
        minus_btn = ft.Container(
            width=36,
            height=36,
            border_radius=18,
            border=ft.border.all(1, theme.LINE_STRONG) if can_adjust else None,
            alignment=ft.Alignment.CENTER,
            on_click=lambda _: self._adjust_duration(-5) if can_adjust else None,
            opacity=1.0 if can_adjust else 0.0,
            content=ft.Icon(ft.Icons.REMOVE_ROUNDED, color=theme.TEXT_PRIMARY, size=20),
        )
        plus_btn = ft.Container(
            width=36,
            height=36,
            border_radius=18,
            border=ft.border.all(1, theme.LINE_STRONG) if can_adjust else None,
            alignment=ft.Alignment.CENTER,
            on_click=lambda _: self._adjust_duration(5) if can_adjust else None,
            opacity=1.0 if can_adjust else 0.0,
            content=ft.Icon(ft.Icons.ADD_ROUNDED, color=theme.TEXT_PRIMARY, size=20),
        )
        ring_row = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            controls=[minus_btn, ring, plus_btn],
        )

        # -- Controls --
        controls = create_timer_controls(
            is_running=is_running,
            is_idle=is_idle,
            on_play_pause=self._on_play_pause,
            on_cancel=self._on_cancel,
        )

        # -- Bottom caption --
        if is_idle:
            bottom_caption = ft.Text(
                "Notifications muted · Tap to start",
                size=CAPTION_FONT_SIZE,
                color=theme.TEXT_SECONDARY,
                text_align=ft.TextAlign.CENTER,
            )
        elif self.timer.status == TimerStatus.COMPLETED:
            earned = max(1, round(self.timer.total_seconds / 60.0 * 0.4))
            bottom_caption = ft.Text(
                f"+{earned} points!",
                size=BODY_FONT_SIZE + 4,
                color=theme.MOSS,
                weight=ft.FontWeight.W_700,
                text_align=ft.TextAlign.CENTER,
            )
        else:
            bottom_caption = ft.Container()

        content_controls = [
            header,
            ft.Container(height=PADDING_MD),
            session_pills,
            ft.Container(height=4),
            session_caption,
            ft.Container(expand=True),
            ft.Container(alignment=ft.Alignment.CENTER, content=ring_row),
            ft.Container(height=PADDING_LG),
            controls,
            ft.Container(height=8),
            bottom_caption,
        ]

        # Test button (only in idle)
        if is_idle:
            content_controls.append(ft.Container(height=4))
            content_controls.append(
                ft.IconButton(
                    icon=ft.Icons.BUG_REPORT_OUTLINED,
                    icon_color=theme.TEXT_SECONDARY,
                    icon_size=18,
                    tooltip=f"Test ({TEST_DURATION_SECONDS}s)",
                    on_click=self._set_test_duration,
                ),
            )

        content_controls.append(ft.Container(expand=True))

        return ft.Column(
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=content_controls,
        )

    def build(self, page: ft.Page) -> ft.Container:
        self._page = page
        page.on_keyboard_event = self._on_keyboard
        self._container = ft.Container(
            expand=True,
            bgcolor=None,
            padding=ft.Padding.only(top=PADDING_XL, bottom=PADDING_LG),
            content=self._build_content(),
        )
        return self._container

    def dispose(self):
        self._stop_tick_loop()
