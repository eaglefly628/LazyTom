"""Mood picker — modal overlay with 4 large emoji-mood buttons.

Flet 0.84.0 doesn't have page.open(); we use a Stack overlay added directly
to page.overlay and toggle visibility instead.
"""

import flet as ft
import theme
from theme import (
    BODY_FONT_SIZE,
    CAPTION_FONT_SIZE,
    PADDING_LG,
    PADDING_MD,
    PADDING_SM,
    SUBTITLE_FONT_SIZE,
)
from mood_engine import MoodLevel, MOOD_LABELS


def show_mood_picker(page: ft.Page, title: str, on_selected):
    """Display a modal mood picker overlay.

    Args:
        page: The Flet page.
        title: Title text shown at the top of the dialog.
        on_selected: Callback `fn(mood: MoodLevel)` invoked once the user picks one.
    """

    container_ref: dict = {}

    def _close():
        ov = container_ref.get("ov")
        if ov is not None and ov in page.overlay:
            page.overlay.remove(ov)
            page.update()

    def _pick(mood: MoodLevel):
        _close()
        if on_selected:
            on_selected(mood)

    mood_order = [
        MoodLevel.ENERGETIC,
        MoodLevel.NORMAL,
        MoodLevel.TIRED,
        MoodLevel.EXHAUSTED,
    ]

    buttons = []
    for mood in mood_order:
        label = MOOD_LABELS[mood]
        btn = ft.Container(
            bgcolor=theme.SURFACE_COLOR,
            border=ft.border.all(1, theme.LINE_STRONG),
            border_radius=14,
            padding=ft.Padding.symmetric(horizontal=PADDING_LG, vertical=PADDING_MD),
            ink=True,
            on_click=lambda _, m=mood: _pick(m),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Text(
                        label,
                        size=SUBTITLE_FONT_SIZE,
                        color=theme.TEXT_PRIMARY,
                        weight=ft.FontWeight.W_600,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
            ),
        )
        buttons.append(btn)

    dialog = ft.Container(
        bgcolor=theme.BG_COLOR,
        border_radius=20,
        padding=ft.Padding.symmetric(horizontal=PADDING_LG, vertical=PADDING_LG),
        width=320,
        content=ft.Column(
            tight=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            spacing=PADDING_SM,
            controls=[
                ft.Text(
                    title,
                    size=SUBTITLE_FONT_SIZE,
                    color=theme.TEXT_PRIMARY,
                    weight=ft.FontWeight.W_700,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=4),
                *buttons,
                ft.Container(height=4),
                ft.TextButton(
                    content=ft.Text(
                        "Cancel",
                        size=CAPTION_FONT_SIZE,
                        color=theme.TEXT_SECONDARY,
                    ),
                    on_click=lambda _: _close(),
                ),
            ],
        ),
    )

    backdrop = ft.Container(
        expand=True,
        bgcolor="#00000080",
        on_click=lambda _: _close(),
    )
    overlay = ft.Stack(
        expand=True,
        controls=[
            backdrop,
            ft.Container(
                expand=True,
                alignment=ft.Alignment.CENTER,
                content=dialog,
            ),
        ],
    )

    container_ref["ov"] = overlay
    page.overlay.append(overlay)
    page.update()
