"""Circular countdown ring — moss-green arc on a paper disc."""

import math
import flet as ft
import flet.canvas as cv

import theme
from theme import TIMER_FONT_SIZE, RING_SIZE, RING_STROKE_WIDTH, CAPTION_FONT_SIZE


def create_countdown_ring(
    formatted_time: str,
    progress: float,
    task_name: str | None = None,
    end_time_str: str | None = None,
) -> ft.Stack:
    """Build a countdown ring with centered content.

    Args:
        formatted_time: Time string like "25:00".
        progress: 1.0 = full, 0.0 = done.
        task_name: Optional task name shown above the time.
        end_time_str: Optional "ends at X:XX PM" shown below the time.
    """
    size = RING_SIZE
    stroke = RING_STROKE_WIDTH

    # Disc radius for the paper-colored center background
    disc_size = size - stroke * 4

    inset = stroke / 2

    # Background track — full circle, subtle line color
    bg_arc = cv.Arc(
        x=inset,
        y=inset,
        width=size - stroke,
        height=size - stroke,
        start_angle=0,
        sweep_angle=2 * math.pi,
        paint=ft.Paint(
            stroke_width=stroke,
            style=ft.PaintingStyle.STROKE,
            color=theme.DIVIDER_COLOR,
        ),
    )

    # Foreground arc — moss green, shrinks with progress
    fg_arc = cv.Arc(
        x=inset,
        y=inset,
        width=size - stroke,
        height=size - stroke,
        start_angle=-math.pi / 2,
        sweep_angle=-2 * math.pi * progress,
        paint=ft.Paint(
            stroke_width=stroke,
            style=ft.PaintingStyle.STROKE,
            color=theme.MOSS,
            stroke_cap=ft.StrokeCap.ROUND,
        ),
    )

    canvas = cv.Canvas(
        width=size,
        height=size,
        shapes=[bg_arc, fg_arc],
    )

    # Build center content
    center_controls = []

    if task_name:
        center_controls.append(
            ft.Text(
                "FOCUS ON",
                size=CAPTION_FONT_SIZE,
                color=theme.TEXT_SECONDARY,
                weight=ft.FontWeight.W_600,
                text_align=ft.TextAlign.CENTER,
            )
        )
        center_controls.append(
            ft.Text(
                task_name,
                size=13,
                color=theme.INK_SOFT,
                weight=ft.FontWeight.W_600,
                text_align=ft.TextAlign.CENTER,
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS,
            )
        )
        center_controls.append(ft.Container(height=4))

    center_controls.append(
        ft.Text(
            formatted_time,
            size=TIMER_FONT_SIZE,
            color=theme.TEXT_PRIMARY,
            weight=ft.FontWeight.W_200,
            text_align=ft.TextAlign.CENTER,
        )
    )

    if end_time_str:
        center_controls.append(
            ft.Text(
                end_time_str,
                size=CAPTION_FONT_SIZE,
                color=theme.TEXT_SECONDARY,
                text_align=ft.TextAlign.CENTER,
            )
        )

    center_column = ft.Column(
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=2,
        controls=center_controls,
    )

    # Paper disc behind center content
    center_disc = ft.Container(
        width=disc_size,
        height=disc_size,
        border_radius=disc_size / 2,
        bgcolor=theme.SURFACE_COLOR,
        alignment=ft.Alignment.CENTER,
        content=center_column,
    )

    return ft.Stack(
        width=size,
        height=size,
        controls=[
            canvas,
            ft.Container(
                width=size,
                height=size,
                alignment=ft.Alignment.CENTER,
                content=center_disc,
            ),
        ],
    )
