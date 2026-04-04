"""Timer control buttons — play/pause and reset."""

import flet as ft

from theme import TEXT_PRIMARY, TEXT_SECONDARY, TOMATO_RED, PADDING_MD


def create_timer_controls(
    is_running: bool,
    is_idle: bool,
    on_play_pause,
    on_reset,
) -> ft.Row:
    """Build the play/pause and reset buttons.

    Args:
        is_running: Whether the timer is currently counting down.
        is_idle: Whether the timer is in idle/reset state.
        on_play_pause: Callback for the play/pause button.
        on_reset: Callback for the reset button.
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

    # Reset button — smaller, secondary action
    reset_btn = ft.IconButton(
        icon=ft.Icons.REPLAY_ROUNDED,
        icon_color=TEXT_SECONDARY if is_idle else TEXT_PRIMARY,
        icon_size=28,
        on_click=on_reset,
        disabled=is_idle,
    )

    return ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=24,
        controls=[reset_btn, play_pause_btn],
    )
