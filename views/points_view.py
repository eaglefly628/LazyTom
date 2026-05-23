"""Points view — 'Your Garden' screen with hero card, weekly chart, and session history."""

from datetime import datetime, timedelta
import flet as ft
import flet.canvas as cv
import math

import theme
from theme import (
    BODY_FONT_SIZE, CAPTION_FONT_SIZE, PADDING_LG, PADDING_MD, PADDING_XL,
    SUBTITLE_FONT_SIZE, PAGE_TITLE_SIZE, HERO_NUMBER_SIZE, PADDING_SM,
)

from points_engine import PointsManager


class PointsView:
    """Points history screen — 'Your Garden' with hero card, weekly chart, history."""

    def __init__(self, points_manager: PointsManager):
        self.points = points_manager
        self._page: ft.Page | None = None
        self._container: ft.Container | None = None

    def rebuild(self):
        """Refresh the view with latest data."""
        if self._page and self._container:
            self._container.content = self._build_content()
            self._page.update()

    def _get_today_points(self) -> int:
        """Sum points earned today."""
        today = datetime.now().date().isoformat()
        total = 0
        for txn in self.points.history:
            if txn.timestamp and txn.timestamp[:10] == today:
                total += txn.amount
        return total

    def _get_weekly_data(self) -> list[int]:
        """Get points per day for the last 7 days (Mon-Sun or last 7)."""
        today = datetime.now().date()
        daily = []
        for i in range(6, -1, -1):
            day = (today - timedelta(days=i)).isoformat()
            pts = sum(
                txn.amount for txn in self.points.history
                if txn.timestamp and txn.timestamp[:10] == day
            )
            daily.append(pts)
        return daily

    def _build_weekly_chart(self, data: list[int]) -> ft.Row:
        """Build a simple 7-bar weekly chart."""
        max_val = max(data) if any(data) else 1
        bar_height = 60
        today_idx = 6  # last bar is today

        day_labels = []
        today = datetime.now().date()
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            day_labels.append(d.strftime("%a")[0])  # M, T, W, ...

        bars = []
        for i, val in enumerate(data):
            h = max(4, int((val / max_val) * bar_height)) if val > 0 else 4
            is_today = i == today_idx
            bar_color = theme.CLAY if is_today else theme.CREAM

            bar = ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
                controls=[
                    ft.Container(expand=True),
                    ft.Container(
                        width=20,
                        height=h,
                        border_radius=4,
                        bgcolor=bar_color,
                    ),
                    ft.Text(
                        day_labels[i],
                        size=9,
                        color=theme.CREAM if not is_today else theme.CLAY,
                        weight=ft.FontWeight.W_600 if is_today else ft.FontWeight.W_400,
                    ),
                ],
            )
            bars.append(ft.Container(expand=True, height=bar_height + 20, content=bar))

        return ft.Row(
            spacing=4,
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            controls=bars,
        )

    def _build_hero_card(self) -> ft.Container:
        """Dark moss gradient hero card with total points and weekly chart."""
        today_pts = self._get_today_points()
        weekly = self._get_weekly_data()

        today_chip = ft.Container(
            bgcolor=theme.LEAF,
            border_radius=10,
            padding=ft.Padding.symmetric(horizontal=8, vertical=2),
            content=ft.Text(
                f"+{today_pts} today",
                size=CAPTION_FONT_SIZE,
                color=theme.MOSS,
                weight=ft.FontWeight.W_600,
            ),
        )

        return ft.Container(
            bgcolor=theme.MOSS,
            border_radius=20,
            padding=PADDING_LG,
            content=ft.Column(
                spacing=PADDING_MD,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(
                                "TOTAL POINTS",
                                size=CAPTION_FONT_SIZE,
                                color=theme.LEAF,
                                weight=ft.FontWeight.W_600,
                            ),
                            today_chip,
                        ],
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.END,
                        spacing=4,
                        controls=[
                            ft.Text(
                                str(self.points.balance),
                                size=HERO_NUMBER_SIZE,
                                color="#FFFFFF",
                                weight=ft.FontWeight.W_700,
                            ),
                            ft.Container(
                                padding=ft.Padding.only(bottom=12),
                                content=ft.Text(
                                    "pts",
                                    size=BODY_FONT_SIZE,
                                    color=theme.LEAF,
                                ),
                            ),
                        ],
                    ),
                    self._build_weekly_chart(weekly),
                ],
            ),
        )

    def _format_history_time(self, timestamp: str) -> str:
        """Format timestamp into a friendly display string."""
        try:
            dt = datetime.fromisoformat(timestamp)
            today = datetime.now().date()
            if dt.date() == today:
                day_part = "Today"
            elif dt.date() == today - timedelta(days=1):
                day_part = "Yesterday"
            else:
                day_part = dt.strftime("%b %d")
            time_part = dt.strftime("%H:%M")
            return f"{day_part} · {time_part}"
        except (ValueError, TypeError):
            return timestamp[:16].replace("T", " ") if timestamp else ""

    def _build_history_row(self, txn, is_last: bool) -> ft.Container:
        """Build a flat history row with colored left bar."""
        time_display = self._format_history_time(txn.timestamp)
        # Extract duration from reason if possible
        duration_str = ""
        if "min" in txn.reason:
            parts = txn.reason.split()
            for i, p in enumerate(parts):
                if p.endswith("min"):
                    duration_str = f" · {p}"
                    break

        row_content = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True,
                    controls=[
                        # Colored difficulty bar on left
                        ft.Container(
                            width=3,
                            height=36,
                            border_radius=2,
                            bgcolor=theme.MOSS,
                        ),
                        ft.Column(
                            spacing=2,
                            expand=True,
                            controls=[
                                ft.Text(
                                    txn.reason,
                                    size=13,
                                    color=theme.TEXT_PRIMARY,
                                    weight=ft.FontWeight.W_600,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                                ft.Text(
                                    f"{time_display}{duration_str}",
                                    size=CAPTION_FONT_SIZE,
                                    color=theme.TEXT_SECONDARY,
                                ),
                            ],
                        ),
                    ],
                ),
                ft.Text(
                    f"+{txn.amount}",
                    size=22,
                    color=theme.MOSS,
                    weight=ft.FontWeight.W_700,
                ),
            ],
        )

        controls = [
            ft.Container(
                padding=ft.Padding.symmetric(vertical=PADDING_SM),
                content=row_content,
            ),
        ]
        if not is_last:
            controls.append(
                ft.Container(
                    height=1,
                    bgcolor=theme.DIVIDER_COLOR,
                ),
            )

        return ft.Container(
            content=ft.Column(spacing=0, controls=controls),
        )

    def _build_content(self) -> ft.Column:
        # Title row
        now = datetime.now()
        month_str = now.strftime("%B").upper()

        title_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text(
                    "Your Garden",
                    size=PAGE_TITLE_SIZE,
                    color=theme.TEXT_PRIMARY,
                    weight=ft.FontWeight.W_700,
                ),
                ft.Text(
                    month_str,
                    size=CAPTION_FONT_SIZE,
                    color=theme.TEXT_SECONDARY,
                    weight=ft.FontWeight.W_600,
                ),
            ],
        )

        # Hero card
        hero = self._build_hero_card()

        # Recent sessions header
        sessions_header = ft.Text(
            "RECENT SESSIONS",
            size=CAPTION_FONT_SIZE,
            color=theme.TEXT_SECONDARY,
            weight=ft.FontWeight.W_600,
        )

        # History list
        history = self.points.get_history()
        if not history:
            history_content = ft.Container(
                padding=PADDING_XL,
                content=ft.Text(
                    "No sessions yet. Complete a focus session to earn points!",
                    size=BODY_FONT_SIZE,
                    color=theme.TEXT_SECONDARY,
                    text_align=ft.TextAlign.CENTER,
                ),
            )
        else:
            history_items = []
            for i, txn in enumerate(history):
                is_last = i == len(history) - 1
                history_items.append(self._build_history_row(txn, is_last))
            history_content = ft.Column(spacing=0, controls=history_items)

        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=PADDING_LG),
                    content=title_row,
                ),
                ft.Container(height=PADDING_MD),
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=PADDING_LG),
                    content=hero,
                ),
                ft.Container(height=PADDING_LG),
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=PADDING_LG),
                    content=sessions_header,
                ),
                ft.Container(height=8),
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=PADDING_LG),
                    content=history_content,
                ),
            ],
        )

    def build(self, page: ft.Page) -> ft.Container:
        """Build the points view."""
        self._page = page
        self._container = ft.Container(
            expand=True,
            bgcolor=None,
            padding=ft.Padding.only(top=PADDING_XL, bottom=PADDING_LG),
            content=self._build_content(),
        )
        return self._container
