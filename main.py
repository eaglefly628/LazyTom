"""LazyTom — A Pomodoro timer with points system.

Run with: flet run main.py
"""

import flet as ft
import theme

from points_engine import PointsManager
from task_engine import TaskManager
from mood_engine import MoodManager
from views.timer_view import TimerView
from views.points_view import PointsView
from views.tasks_view import TasksView
from views.settings_view import SettingsView
import storage

def main(page: ft.Page):
    # Load saved theme before any UI is built
    saved_settings = storage.load_settings()
    saved_theme = saved_settings.get("theme")
    if saved_theme:
        try:
            theme.set_theme(theme.ThemeName(saved_theme))
        except ValueError:
            pass

    page.title = "LazyTom"
    page.bgcolor = theme.BG_COLOR
    page.padding = 0
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

    mood_mgr = MoodManager()
    saved_mood = storage.load_mood()
    if saved_mood:
        mood_mgr.load_from_dict(saved_mood)

    # ── Views ────────────────────────────────────────────
    def on_points_changed():
        points_view.rebuild()

    def on_settings_changed():
        settings = storage.load_settings()
        timer_view.timer.set_duration(settings.get("focus_minutes", 25))
        timer_view._rebuild()

    def on_theme_changed():
        # Rebuild everything when theme switches
        page.bgcolor = theme.BG_COLOR
        bg_image.src = theme.BG_IMAGE
        nav_bar.bgcolor = theme.BG_COLOR
        nav_bar.indicator_color = theme.TOMATO_RED
        timer_view._rebuild()
        points_view.rebuild()
        tasks_view.rebuild()
        page.update()

    def on_task_selected(task):
        timer_view.set_current_task(task)
        switch_tab(0)
        nav_bar.selected_index = 0
        page.update()

    timer_view = TimerView(points, mood_manager=mood_mgr, on_points_changed=on_points_changed)
    points_view = PointsView(points)
    tasks_view = TasksView(task_mgr, mood_manager=mood_mgr, on_task_selected=on_task_selected)
    settings_view = SettingsView(
        on_settings_changed=on_settings_changed,
        on_theme_changed=on_theme_changed,
    )

    # Build view controls
    timer_control = timer_view.build(page)
    points_control = points_view.build(page)
    tasks_control = tasks_view.build(page)
    settings_control = settings_view.build(page)

    # ── Content area with theme background image ────────
    bg_image = ft.Image(
        src=theme.BG_IMAGE,
        fit=ft.BoxFit.COVER,
        expand=True,
    )
    bg_overlay = ft.Container(
        expand=True,
        bgcolor="#00000040",  # subtle dark overlay for readability
    )
    content_inner = ft.Container(expand=True, content=timer_control)

    content = ft.Stack(
        expand=True,
        controls=[bg_image, bg_overlay, content_inner],
    )

    def switch_tab(index: int):
        views = [timer_control, points_control, tasks_control, settings_control]
        content_inner.content = views[index]
        if index == 1:
            points_view.rebuild()
        if index == 2:
            tasks_view.rebuild()
        page.update()

    # ── Bottom navigation ────────────────────────────────
    nav_bar = ft.NavigationBar(
        bgcolor=theme.BG_COLOR,
        indicator_color=theme.TOMATO_RED,
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
