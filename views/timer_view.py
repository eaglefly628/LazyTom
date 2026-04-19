"""Timer view — the main screen with countdown ring and controls."""

import asyncio
import flet as ft

from theme import (
    BG_COLOR,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TOMATO_RED,
    TITLE_FONT_SIZE,
    BODY_FONT_SIZE,
    CAPTION_FONT_SIZE,
    PADDING_LG,
    PADDING_XL,
    SURFACE_COLOR,
)
from timer_engine import PomodoroTimer, TimerStatus
from points_engine import PointsManager
from components.countdown_ring import create_countdown_ring
from components.timer_controls import create_timer_controls
from components.points_badge import create_points_badge
import storage

RENDER_FPS = 30
TEST_DURATION_SECONDS = 10


class TimerView:
    """Main timer screen with countdown ring, controls, and points badge."""

    def __init__(self, points_manager: PointsManager, on_points_changed=None):
        self.timer = PomodoroTimer(duration_minutes=25)
        self.points = points_manager
        self.on_points_changed = on_points_changed
        self._is_ticking = False
        self._page: ft.Page | None = None
        self._container: ft.Container | None = None
        self._seconds_since_tick = 0.0
        self._current_task = None

        settings = storage.load_settings()
        duration = settings.get("focus_minutes", 25)
        self.timer.set_duration(duration)

        self.timer.on_complete = self._on_timer_complete

    def _on_timer_complete(self):
        self._is_ticking = False
        duration_min = self.timer.total_seconds / 60.0
        self.points.award_for_pomodoro(max(1, round(duration_min)))
        storage.save_points(self.points.to_dict())
        if self.on_points_changed:
            self.on_points_changed()
        self._rebuild()

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

    def _on_play_pause(self, e):
        if self.timer.status == TimerStatus.RUNNING:
            self.timer.pause()
            self._stop_tick_loop()
        elif self.timer.status in (TimerStatus.IDLE, TimerStatus.COMPLETED, TimerStatus.PAUSED):
            self.timer.start()
            self._start_tick_loop()
        self._rebuild()

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
        """Set the task to work on. Shows task name on timer screen."""
        self._current_task = task
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
        if self._current_task and self.timer.status in (TimerStatus.RUNNING, TimerStatus.PAUSED):
            return self._current_task.name
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

        ring = create_countdown_ring(
            self.timer.formatted_time,
            self.timer.smooth_progress,
        )

        can_adjust = is_idle
        minus_btn = ft.IconButton(
            icon=ft.Icons.REMOVE_ROUNDED,
            icon_color=TEXT_PRIMARY if can_adjust else TEXT_SECONDARY,
            icon_size=28,
            on_click=lambda _: self._adjust_duration(-5),
            disabled=not can_adjust or self.timer.total_seconds <= 60,
            opacity=1.0 if can_adjust else 0.0,
        )
        plus_btn = ft.IconButton(
            icon=ft.Icons.ADD_ROUNDED,
            icon_color=TEXT_PRIMARY if can_adjust else TEXT_SECONDARY,
            icon_size=28,
            on_click=lambda _: self._adjust_duration(5),
            disabled=not can_adjust,
            opacity=1.0 if can_adjust else 0.0,
        )
        ring_row = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            controls=[minus_btn, ring, plus_btn],
        )

        controls = create_timer_controls(
            is_running=is_running,
            is_idle=is_idle,
            on_play_pause=self._on_play_pause,
            on_cancel=self._on_cancel,
        )

        status = ft.Text(
            self._status_text(),
            size=BODY_FONT_SIZE,
            color=TOMATO_RED if self.timer.status == TimerStatus.COMPLETED else TEXT_SECONDARY,
            text_align=ft.TextAlign.CENTER,
        )

        # Test button — small, only visible when idle
        test_btn = ft.ElevatedButton(
            visible=is_idle,
            on_click=self._set_test_duration,
            bgcolor=SURFACE_COLOR,
            color=TEXT_SECONDARY,
            content=ft.Text(f"Test ({TEST_DURATION_SECONDS}s)", size=CAPTION_FONT_SIZE),
        )

        completed_text = None
        if self.timer.status == TimerStatus.COMPLETED:
            earned = max(1, round(self.timer.total_seconds / 60.0 * 0.4))
            completed_text = ft.Text(
                f"+{earned} points!",
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
            ft.Container(alignment=ft.Alignment.CENTER, content=ring_row),
            ft.Container(height=PADDING_XL),
            controls,
            ft.Container(height=12),
            status,
        ]

        if completed_text:
            content_controls.insert(-1, completed_text)

        content_controls.append(ft.Container(expand=True))
        content_controls.append(test_btn)

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
            bgcolor=BG_COLOR,
            padding=ft.Padding.only(top=PADDING_XL, bottom=PADDING_LG),
            content=self._build_content(),
        )
        return self._container

    def dispose(self):
        self._stop_tick_loop()
