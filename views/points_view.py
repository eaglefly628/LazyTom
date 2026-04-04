"""Points view — shows balance and transaction history."""

import flet as ft

from theme import (
    BG_COLOR,
    SURFACE_COLOR,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TOMATO_RED,
    TITLE_FONT_SIZE,
    SUBTITLE_FONT_SIZE,
    BODY_FONT_SIZE,
    CAPTION_FONT_SIZE,
    PADDING_MD,
    PADDING_LG,
    PADDING_XL,
)
from points_engine import PointsManager


class PointsView:
    """Points history screen showing balance and all transactions."""

    def __init__(self, points_manager: PointsManager):
        self.points = points_manager
        self._page: ft.Page | None = None
        self._container: ft.Container | None = None

    def rebuild(self):
        """Refresh the view with latest data."""
        if self._page and self._container:
            self._container.content = self._build_content()
            self._page.update()

    def _build_content(self) -> ft.Column:
        # Balance card
        balance_card = ft.Container(
            bgcolor=SURFACE_COLOR,
            border_radius=16,
            padding=PADDING_LG,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
                controls=[
                    ft.Text(
                        "Total Points",
                        size=BODY_FONT_SIZE,
                        color=TEXT_SECONDARY,
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.LOCAL_FIRE_DEPARTMENT, color=TOMATO_RED, size=32),
                            ft.Text(
                                str(self.points.balance),
                                size=48,
                                color=TEXT_PRIMARY,
                                weight=ft.FontWeight.W_700,
                            ),
                        ],
                    ),
                ],
            ),
        )

        # History header
        history_header = ft.Text(
            "History",
            size=SUBTITLE_FONT_SIZE,
            color=TEXT_PRIMARY,
            weight=ft.FontWeight.W_600,
        )

        # History list
        history = self.points.get_history()
        if not history:
            history_content = ft.Container(
                padding=PADDING_XL,
                content=ft.Text(
                    "No points yet. Complete a focus session to earn points!",
                    size=BODY_FONT_SIZE,
                    color=TEXT_SECONDARY,
                    text_align=ft.TextAlign.CENTER,
                ),
            )
        else:
            history_items = []
            for txn in history:
                # Parse timestamp for display
                time_display = txn.timestamp[:16].replace("T", " ") if txn.timestamp else ""
                item = ft.Container(
                    bgcolor=SURFACE_COLOR,
                    border_radius=12,
                    padding=PADDING_MD,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(
                                        txn.reason,
                                        size=BODY_FONT_SIZE,
                                        color=TEXT_PRIMARY,
                                    ),
                                    ft.Text(
                                        time_display,
                                        size=CAPTION_FONT_SIZE,
                                        color=TEXT_SECONDARY,
                                    ),
                                ],
                            ),
                            ft.Text(
                                f"+{txn.amount}",
                                size=SUBTITLE_FONT_SIZE,
                                color=TOMATO_RED,
                                weight=ft.FontWeight.W_700,
                            ),
                        ],
                    ),
                )
                history_items.append(item)
            history_content = ft.Column(spacing=8, controls=history_items)

        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=PADDING_LG),
                    content=ft.Text(
                        "Points",
                        size=TITLE_FONT_SIZE,
                        color=TEXT_PRIMARY,
                        weight=ft.FontWeight.W_700,
                    ),
                ),
                ft.Container(height=PADDING_MD),
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=PADDING_LG),
                    content=balance_card,
                ),
                ft.Container(height=PADDING_LG),
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=PADDING_LG),
                    content=history_header,
                ),
                ft.Container(height=8),
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=PADDING_LG),
                    content=history_content,
                ),
            ],
        )

    def build(self, page: ft.Page) -> ft.Container:
        """Build the points view."""
        self._page = page
        self._container = ft.Container(
            expand=True,
            bgcolor=BG_COLOR,
            padding=ft.padding.only(top=PADDING_XL, bottom=PADDING_LG),
            content=self._build_content(),
        )
        return self._container
