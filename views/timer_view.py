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
        self._is_ticking = False
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
        self._is_ticking = False
        self.points.award_for_pomodoro(self.timer.duration_minutes)
        storage.save_points(self.points.to_dict())
        if self.on_points_changed:
            self.on_points_changed()
        self._rebuild()

    async def _tick_loop(self):
        """Async tick loop running in Flet's event loop — safe for UI updates."""
        while self._is_ticking and self.timer.status == TimerStatus.RUNNING:
            await asyncio.sleep(1)
            if self._is_ticking and self.timer.status == TimerStatus.RUNNING:
                self.timer.tick()
                self._rebuild()

    def _start_tick_loop(self):
        """Schedule the async tick loop on Flet's event loop."""
        if self._is_ticking:
            return
        self._is_ticking = True
        if self._page:
            self._page.run_task(self._tick_loop)

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
        """Cancel the current session — stop timer and go back to idle."""
        self._stop_tick_loop()
        self.timer.reset()
        self._rebuild()

    def _adjust_duration(self, delta: int):
        """Adjust timer duration by delta minutes. Only when idle."""
        if self.timer.status == TimerStatus.IDLE:
            self.timer.adjust_duration(delta)
            storage.save_settings({
                "focus_minutes": self.timer.duration_minutes,
                "break_minutes": storage.load_settings().get("break_minutes", 5),
            })
            self._rebuild()

    def _on_keyboard(self, e: ft.KeyboardEvent):
        """Handle keyboard shortcuts — up/down arrows ±5 min."""
        if e.key == "Arrow Up":
            self._adjust_duration(5)
        elif e.key == "Arrow Down":
            self._adjust_duration(-5)

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

        # Countdown ring with ±5min buttons on left/right (only when idle)
        ring = create_countdown_ring(
            self.timer.formatted_time,
            self.timer.progress,
        )

        can_adjust = self.timer.status == TimerStatus.IDLE
        minus_btn = ft.IconButton(
            icon=ft.Icons.REMOVE_ROUNDED,
            icon_color=TEXT_PRIMARY if can_adjust else TEXT_SECONDARY,
            icon_size=28,
            on_click=lambda _: self._adjust_duration(-5),
            disabled=not can_adjust or self.timer.duration_minutes <= 5,
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
            ft.Container(alignment=ft.Alignment.CENTER, content=ring_row),
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
        page.on_keyboard_event = self._on_keyboard
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
