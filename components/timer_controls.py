"""Timer control buttons — pill-style Begin Focus / Pause / Cancel."""

import flet as ft
import theme
from theme import PADDING_MD, BODY_FONT_SIZE


def create_timer_controls(
    is_running: bool,
    is_idle: bool,
    on_play_pause,
    on_cancel,
) -> ft.Column:
    """Build the timer control buttons.

    - Idle: "Begin Focus" moss pill button (no cancel visible)
    - Running: "Pause" pill + cancel icon
    - Paused: "Resume" pill + cancel icon

    Args:
        is_running: Whether the timer is currently counting down.
        is_idle: Whether the timer is in idle/reset state.
        on_play_pause: Callback for the play/pause button.
        on_cancel: Callback for the cancel button.
    """
    controls = []

    if is_idle:
        # Big inviting "Begin Focus" pill — moss green
        begin_btn = ft.Container(
            bgcolor=theme.MOSS,
            border_radius=28,
            padding=ft.Padding.symmetric(horizontal=32, vertical=14),
            ink=True,
            on_click=on_play_pause,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
                controls=[
                    ft.Icon(ft.Icons.PLAY_ARROW_ROUNDED, color=theme.CREAM, size=24),
                    ft.Text(
                        "Begin Focus",
                        size=BODY_FONT_SIZE + 2,
                        color=theme.CREAM,
                        weight=ft.FontWeight.W_600,
                    ),
                ],
            ),
        )
        controls.append(begin_btn)
    elif is_running:
        # Running state: Pause pill + cancel
        pause_btn = ft.Container(
            bgcolor=theme.CLAY,
            border_radius=28,
            padding=ft.Padding.symmetric(horizontal=32, vertical=14),
            ink=True,
            on_click=on_play_pause,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
                controls=[
                    ft.Icon(ft.Icons.PAUSE_ROUNDED, color=theme.CREAM, size=24),
                    ft.Text(
                        "Pause",
                        size=BODY_FONT_SIZE + 2,
                        color=theme.CREAM,
                        weight=ft.FontWeight.W_600,
                    ),
                ],
            ),
        )
        cancel_btn = ft.TextButton(
            content=ft.Text(
                "Cancel",
                size=BODY_FONT_SIZE,
                color=theme.TEXT_SECONDARY,
            ),
            on_click=on_cancel,
        )
        controls.append(pause_btn)
        controls.append(ft.Container(height=4))
        controls.append(cancel_btn)
    else:
        # Paused state: Resume pill + cancel
        resume_btn = ft.Container(
            bgcolor=theme.MOSS,
            border_radius=28,
            padding=ft.Padding.symmetric(horizontal=32, vertical=14),
            ink=True,
            on_click=on_play_pause,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
                controls=[
                    ft.Icon(ft.Icons.PLAY_ARROW_ROUNDED, color=theme.CREAM, size=24),
                    ft.Text(
                        "Resume",
                        size=BODY_FONT_SIZE + 2,
                        color=theme.CREAM,
                        weight=ft.FontWeight.W_600,
                    ),
                ],
            ),
        )
        cancel_btn = ft.TextButton(
            content=ft.Text(
                "Cancel",
                size=BODY_FONT_SIZE,
                color=theme.TEXT_SECONDARY,
            ),
            on_click=on_cancel,
        )
        controls.append(resume_btn)
        controls.append(ft.Container(height=4))
        controls.append(cancel_btn)

    return ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0,
        controls=controls,
    )
