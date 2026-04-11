"""Timer control buttons — play/pause and cancel."""

import flet as ft

from theme import TEXT_PRIMARY, TEXT_SECONDARY, TOMATO_RED, PADDING_MD


def create_timer_controls(
    is_running: bool,
    is_idle: bool,
    on_play_pause,
    on_cancel,
) -> ft.Row:
    """Build the play/pause and cancel buttons.

    Args:
        is_running: Whether the timer is currently counting down.
        is_idle: Whether the timer is in idle/reset state.
        on_play_pause: Callback for the play/pause button.
        on_cancel: Callback for the cancel button.
    """
    # Play/pause button — larger, primary action
    play_pause_icon = ft.Icons.PAUSE_ROUNDED if is_running else ft.Icons.PLAY_ARROW_ROUNDED
    play_pause_btn = ft.IconButton(
        icon=play_pause_icon,
        icon_color=TEXT_PRIMARY,
        icon_size=48,
        on_click=on_play_pause,
        style=ft.ButtonStyle(
            shape=ft.CircleBorder(),
            bgcolor=TOMATO_RED,
            padding=PADDING_MD,
        ),
    )

    # Cancel button — stop current session, only visible when timer is active
    cancel_btn = ft.IconButton(
        icon=ft.Icons.CLOSE_ROUNDED,
        icon_color=TEXT_SECONDARY if is_idle else TEXT_PRIMARY,
        icon_size=28,
        on_click=on_cancel,
        disabled=is_idle,
    )

    return ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=24,
        controls=[cancel_btn, play_pause_btn],
    )
