"""Timer view — the main screen with countdown ring and controls."""

import threading
import time
import flet as ft

from theme import (
    BG_COLOR,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TOMATO_RED,
    TITLE_FONT_SIZE,
    BODY_FONT_SIZE,
    PADDING_LG,
    PADDING_XL,
)
from timer_engine import PomodoroTimer, TimerStatus
from points_engine import PointsManager
from components.countdown_ring import create_countdown_ring
from components.timer_controls import create_timer_controls
from components.points_badge import create_points_badge
import storage


class TimerView:
    """Main timer screen with countdown ring, controls, and points badge."""

    def __init__(self, points_manager: PointsManager, on_points_changed=None):
        self.timer = PomodoroTimer(duration_minutes=25)
        self.points = points_manager
        self.on_points_changed = on_points_changed
        self._tick_thread: threading.Thread | None = None
        self._running_flag = threading.Event()
        self._page: ft.Page | None = None
        self._container: ft.Container | None = None

        # Load saved duration
        settings = storage.load_settings()
        duration = settings.get("focus_minutes", 25)
        self.timer.set_duration(duration)

        # Wire up completion callback
        self.timer.on_complete = self._on_timer_complete

    def _on_timer_complete(self):
        """Called when a Pomodoro session finishes."""
        self._stop_tick_loop()
        self.points.award_for_pomodoro(self.timer.duration_minutes)
        storage.save_points(self.points.to_dict())
        if self.on_points_changed:
            self.on_points_changed()
        self._rebuild()

    def _start_tick_loop(self):
        """Start a background thread that ticks every second."""
        if self._running_flag.is_set():
            return
        self._running_flag.set()

        def _loop():
            while self._running_flag.is_set() and self.timer.status == TimerStatus.RUNNING:
                time.sleep(1)
                if self._running_flag.is_set() and self.timer.status == TimerStatus.RUNNING:
                    self.timer.tick()
                    self._rebuild()

        self._tick_thread = threading.Thread(target=_loop, daemon=True)
        self._tick_thread.start()

    def _stop_tick_loop(self):
        self._running_flag.clear()
        self._tick_thread = None

    def _on_play_pause(self, e):
        if self.timer.status == TimerStatus.RUNNING:
            self.timer.pause()
            self._stop_tick_loop()
        elif self.timer.status in (TimerStatus.IDLE, TimerStatus.COMPLETED, TimerStatus.PAUSED):
            self.timer.start()
            self._start_tick_loop()
        self._rebuild()

    def _on_cancel(self, e):
        """Cancel the current session — stop timer and go back to idle."""
        self._stop_tick_loop()
        self.timer.reset()
        self._rebuild()

    def _rebuild(self):
        """Rebuild and update the UI."""
        if self._page and self._container:
            self._container.content = self._build_content()
            self._page.update()

    def _status_text(self) -> str:
        status_map = {
            TimerStatus.IDLE: "Ready to focus",
            TimerStatus.RUNNING: "Focusing...",
            TimerStatus.PAUSED: "Paused",
            TimerStatus.COMPLETED: "Well done!",
        }
        return status_map.get(self.timer.status, "")

    def _build_content(self) -> ft.Column:
        is_running = self.timer.status == TimerStatus.RUNNING
        is_idle = self.timer.status == TimerStatus.IDLE

        # Top bar
        top_bar = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text(
                    "LazyTom",
                    size=TITLE_FONT_SIZE,
                    color=TEXT_PRIMARY,
                    weight=ft.FontWeight.W_700,
                ),
                create_points_badge(self.points.balance),
            ],
        )

        # Countdown ring
        ring = create_countdown_ring(
            self.timer.formatted_time,
            self.timer.progress,
        )

        # Controls
        controls = create_timer_controls(
            is_running=is_running,
            is_idle=is_idle,
            on_play_pause=self._on_play_pause,
            on_cancel=self._on_cancel,
        )

        # Status text
        status = ft.Text(
            self._status_text(),
            size=BODY_FONT_SIZE,
            color=TOMATO_RED if self.timer.status == TimerStatus.COMPLETED else TEXT_SECONDARY,
            text_align=ft.TextAlign.CENTER,
        )

        # Completed bonus text
        completed_text = None
        if self.timer.status == TimerStatus.COMPLETED:
            points_earned = max(1, round(self.timer.duration_minutes * 0.4))
            completed_text = ft.Text(
                f"+{points_earned} points!",
                size=TITLE_FONT_SIZE,
                color=TOMATO_RED,
                weight=ft.FontWeight.W_700,
                text_align=ft.TextAlign.CENTER,
            )

        content_controls = [
            ft.Container(
                padding=ft.Padding.symmetric(horizontal=PADDING_LG),
                content=top_bar,
            ),
            ft.Container(expand=True),
            ft.Container(alignment=ft.Alignment.CENTER, content=ring),
            ft.Container(height=PADDING_XL),
            controls,
            ft.Container(height=12),
            status,
        ]

        if completed_text:
            content_controls.insert(-1, completed_text)

        content_controls.append(ft.Container(expand=True))

        return ft.Column(
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=content_controls,
        )

    def build(self, page: ft.Page) -> ft.Container:
        """Build the timer view. Call this once to get the root control."""
        self._page = page
        self._container = ft.Container(
            expand=True,
            bgcolor=BG_COLOR,
            padding=ft.Padding.only(top=PADDING_XL, bottom=PADDING_LG),
            content=self._build_content(),
        )
        return self._container

    def dispose(self):
        """Clean up resources."""
        self._stop_tick_loop()
