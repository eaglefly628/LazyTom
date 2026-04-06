"""Circular countdown ring component — draws a tomato-red arc that shrinks as time passes."""

import math
import flet as ft
import flet.canvas as cv

from theme import (
    TOMATO_RED,
    TOMATO_RED_DIM,
    TEXT_PRIMARY,
    RING_SIZE,
    RING_STROKE_WIDTH,
    TIMER_FONT_SIZE,
)


def create_countdown_ring(formatted_time: str, progress: float) -> ft.Stack:
    """Build a countdown ring with the time displayed in the center.

    Args:
        formatted_time: Time string like "25:00".
        progress: 1.0 = full, 0.0 = done.
    """
    size = RING_SIZE
    stroke = RING_STROKE_WIDTH
    inset = stroke / 2

    # Background track — full circle, dimmed
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
            color=TOMATO_RED_DIM,
        ),
    )

    # Foreground arc — tomato red, shrinks with progress
    fg_arc = cv.Arc(
        x=inset,
        y=inset,
        width=size - stroke,
        height=size - stroke,
        start_angle=-math.pi / 2,  # start at 12 o'clock
        sweep_angle=-2 * math.pi * progress,  # counter-clockwise
        paint=ft.Paint(
            stroke_width=stroke,
            style=ft.PaintingStyle.STROKE,
            color=TOMATO_RED,
            stroke_cap=ft.StrokeCap.ROUND,
        ),
    )

    canvas = cv.Canvas(
        width=size,
        height=size,
        shapes=[bg_arc, fg_arc],
    )

    # Time text centered over the ring
    time_text = ft.Text(
        formatted_time,
        size=TIMER_FONT_SIZE,
        color=TEXT_PRIMARY,
        weight=ft.FontWeight.W_200,
        text_align=ft.TextAlign.CENTER,
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
                content=time_text,
            ),
        ],
    )
