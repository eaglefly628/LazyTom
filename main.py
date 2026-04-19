"""LazyTom — A Pomodoro timer with points system.

Run with: flet run main.py
"""

import flet as ft

from theme import BG_COLOR, TEXT_PRIMARY, TEXT_SECONDARY, TOMATO_RED
from points_engine import PointsManager
from task_engine import TaskManager
from views.timer_view import TimerView
from views.points_view import PointsView
from views.tasks_view import TasksView
from views.settings_view import SettingsView
import storage


def main(page: ft.Page):
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

    task_mgr = TaskManager()
    saved_tasks = storage.load_tasks()
    if saved_tasks:
        task_mgr.load_from_dict(saved_tasks)

    # ── Views ────────────────────────────────────────────
    def on_points_changed():
        points_view.rebuild()

    def on_settings_changed():
        settings = storage.load_settings()
        timer_view.timer.set_duration(settings.get("focus_minutes", 25))
        timer_view._rebuild()

    def on_task_selected(task):
        timer_view.set_current_task(task)
        switch_tab(0)
        nav_bar.selected_index = 0
        page.update()

    timer_view = TimerView(points, on_points_changed=on_points_changed)
    points_view = PointsView(points)
    tasks_view = TasksView(task_mgr, on_task_selected=on_task_selected)
    settings_view = SettingsView(on_settings_changed=on_settings_changed)

    # Build view controls
    timer_control = timer_view.build(page)
    points_control = points_view.build(page)
    tasks_control = tasks_view.build(page)
    settings_control = settings_view.build(page)

    # ── Content area ─────────────────────────────────────
    content = ft.Container(expand=True, content=timer_control)

    def switch_tab(index: int):
        views = [timer_control, points_control, tasks_control, settings_control]
        content.content = views[index]
        if index == 1:
            points_view.rebuild()
        if index == 2:
            tasks_view.rebuild()
        page.update()

    # ── Bottom navigation ────────────────────────────────
    nav_bar = ft.NavigationBar(
        bgcolor=BG_COLOR,
        indicator_color=TOMATO_RED,
        selected_index=0,
        on_change=lambda e: switch_tab(e.control.selected_index),
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.TIMER_OUTLINED,
                selected_icon=ft.Icons.TIMER,
                label="Timer",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.STARS_OUTLINED,
                selected_icon=ft.Icons.STARS,
                label="Points",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.CHECKLIST_OUTLINED,
                selected_icon=ft.Icons.CHECKLIST,
                label="Tasks",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                label="Settings",
            ),
        ],
    )

    page.add(content, nav_bar)


if __name__ == "__main__":
    ft.app(target=main)
