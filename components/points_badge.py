"""Points balance badge — shows current points in the top bar."""

import flet as ft
import theme
from theme import CAPTION_FONT_SIZE, PADDING_SM

def create_points_badge(balance: int) -> ft.Container:
    """Build a compact points badge showing the current balance."""
    return ft.Container(
        bgcolor=theme.SURFACE_COLOR,
        border_radius=12,
        padding=ft.Padding.symmetric(horizontal=PADDING_SM + 4, vertical=PADDING_SM),
        content=ft.Row(
            spacing=4,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.LOCAL_FIRE_DEPARTMENT, color=theme.TOMATO_RED, size=16),
                ft.Text(
                    str(balance),
                    size=CAPTION_FONT_SIZE + 2,
                    color=theme.TEXT_PRIMARY,
                    weight=ft.FontWeight.W_600,
                ),
            ],
        ),
    )
