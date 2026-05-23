"""Points badge / streak chip — cream pill with flame icon."""

import flet as ft
import theme
from theme import CAPTION_FONT_SIZE, PADDING_SM


def create_points_badge(balance: int, streak_days: int = 0) -> ft.Container:
    """Build a streak chip in the header.

    Shows a cream-colored pill with a flame icon and streak text.
    Falls back to showing balance if no streak.
    """
    if streak_days > 0:
        label = f"{streak_days} DAY STREAK"
    else:
        label = str(balance)

    return ft.Container(
        bgcolor=theme.CREAM,
        border_radius=14,
        padding=ft.Padding.symmetric(horizontal=PADDING_SM + 4, vertical=6),
        content=ft.Row(
            spacing=4,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.LOCAL_FIRE_DEPARTMENT, color=theme.CLAY, size=16),
                ft.Text(
                    label,
                    size=CAPTION_FONT_SIZE,
                    color=theme.INK_SOFT,
                    weight=ft.FontWeight.W_600,
                ),
            ],
        ),
    )
