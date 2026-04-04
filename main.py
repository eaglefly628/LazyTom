"""LazyTom — A Pomodoro timer with points system.

Run with: flet run main.py
"""

import flet as ft

from theme import BG_COLOR, TEXT_PRIMARY, TEXT_SECONDARY, TOMATO_RED
from points_engine import PointsManager
from views.timer_view import TimerView
from views.points_view import PointsView
from views.settings_view import SettingsView
import storage


def main(page: ft.Page):
    # ── Page setup ───────────────────────────────────────
    page.title = "LazyTom"
    page.bgcolor = BG_COLOR
    page.padding = 0
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 400
    page.window.height = 720

    # ── Shared state ─────────────────────────────────────
    points = PointsManager()
    saved_points = storage.load_points()
    if saved_points:
        points.load_from_dict(saved_points)

    # ── Views ────────────────────────────────────────────
    def on_points_changed():
        points_view.rebuild()

    def on_settings_changed():
        settings = storage.load_settings()
        timer_view.timer.set_duration(settings.get("focus_minutes", 25))
        timer_view._rebuild()

    timer_view = TimerView(points, on_points_changed=on_points_changed)
    points_view = PointsView(points)
    settings_view = SettingsView(on_settings_changed=on_settings_changed)

    # Build view controls
    timer_control = timer_view.build(page)
    points_control = points_view.build(page)
    settings_control = settings_view.build(page)

    # ── Content area ─────────────────────────────────────
    content = ft.Container(expand=True, content=timer_control)

    def switch_tab(index: int):
        views = [timer_control, points_control, settings_control]
        content.content = views[index]
        # Refresh points view when switching to it
        if index == 1:
            points_view.rebuild()
        page.update()

    # ── Bottom navigation ────────────────────────────────
    nav_bar = ft.NavigationBar(
        bgcolor=BG_COLOR,
        indicator_color=TOMATO_RED,
        selected_index=0,
        on_change=lambda e: switch_tab(e.control.selected_index),
        destinations=[
            ft.NavigationDestination(
                icon=ft.Icons.TIMER_OUTLINED,
                selected_icon=ft.Icons.TIMER,
                label="Timer",
            ),
            ft.NavigationDestination(
                icon=ft.Icons.STARS_OUTLINED,
                selected_icon=ft.Icons.STARS,
                label="Points",
            ),
            ft.NavigationDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                label="Settings",
            ),
        ],
    )

    # ── Page layout ──────────────────────────────────────
    page.add(content, nav_bar)


if __name__ == "__main__":
    ft.app(target=main)
