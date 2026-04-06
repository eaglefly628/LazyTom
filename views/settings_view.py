"""Settings view — configure focus duration, break duration, and view points rules."""

import flet as ft

from theme import (
    BG_COLOR,
    SURFACE_COLOR,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TOMATO_RED,
    TITLE_FONT_SIZE,
    SUBTITLE_FONT_SIZE,
    BODY_FONT_SIZE,
    CAPTION_FONT_SIZE,
    PADDING_MD,
    PADDING_LG,
    PADDING_XL,
    DIVIDER_COLOR,
)
import storage

# Available duration options
FOCUS_OPTIONS = [15, 20, 25, 30, 45, 60]
BREAK_OPTIONS = [5, 10, 15]


class SettingsView:
    """Settings screen for configuring timer durations."""

    def __init__(self, on_settings_changed=None):
        self.on_settings_changed = on_settings_changed
        self._page: ft.Page | None = None
        self._container: ft.Container | None = None

        # Load current settings
        settings = storage.load_settings()
        self.focus_minutes = settings.get("focus_minutes", 25)
        self.break_minutes = settings.get("break_minutes", 5)

    def _save(self):
        storage.save_settings({
            "focus_minutes": self.focus_minutes,
            "break_minutes": self.break_minutes,
        })
        if self.on_settings_changed:
            self.on_settings_changed()

    def _on_focus_changed(self, e):
        self.focus_minutes = int(e.control.value)
        self._save()
        self._rebuild()

    def _on_break_changed(self, e):
        self.break_minutes = int(e.control.value)
        self._save()
        self._rebuild()

    def _rebuild(self):
        if self._page and self._container:
            self._container.content = self._build_content()
            self._page.update()

    def _build_option_chips(self, options, selected, on_change) -> ft.Row:
        """Build a row of selectable chips for duration options."""
        chips = []
        for opt in options:
            is_selected = opt == selected
            chip = ft.Container(
                bgcolor=TOMATO_RED if is_selected else SURFACE_COLOR,
                border_radius=20,
                padding=ft.Padding.symmetric(horizontal=16, vertical=8),
                on_click=lambda e, v=opt: on_change(
                    type("Event", (), {"control": type("Ctrl", (), {"value": v})()})()
                ),
                content=ft.Text(
                    f"{opt} min",
                    size=BODY_FONT_SIZE,
                    color=TEXT_PRIMARY,
                    weight=ft.FontWeight.W_600 if is_selected else ft.FontWeight.W_400,
                ),
            )
            chips.append(chip)
        return ft.Row(wrap=True, spacing=8, controls=chips)

    def _build_section(self, title: str, subtitle: str, content: ft.Control) -> ft.Container:
        return ft.Container(
            bgcolor=SURFACE_COLOR,
            border_radius=16,
            padding=PADDING_LG,
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Text(title, size=SUBTITLE_FONT_SIZE, color=TEXT_PRIMARY, weight=ft.FontWeight.W_600),
                    ft.Text(subtitle, size=CAPTION_FONT_SIZE, color=TEXT_SECONDARY),
                    content,
                ],
            ),
        )

    def _build_content(self) -> ft.Column:
        # Focus duration
        focus_section = self._build_section(
            "Focus Duration",
            "How long each Pomodoro session lasts",
            self._build_option_chips(FOCUS_OPTIONS, self.focus_minutes, self._on_focus_changed),
        )

        # Break duration
        break_section = self._build_section(
            "Break Duration",
            "Rest time between sessions",
            self._build_option_chips(BREAK_OPTIONS, self.break_minutes, self._on_break_changed),
        )

        # Points rules (read-only info)
        points_per_session = max(1, round(self.focus_minutes * 0.4))
        rules_section = self._build_section(
            "Points Rules",
            "How points are calculated",
            ft.Column(
                spacing=4,
                controls=[
                    ft.Text(
                        f"Complete a {self.focus_minutes}-minute session = {points_per_session} points",
                        size=BODY_FONT_SIZE,
                        color=TOMATO_RED,
                        weight=ft.FontWeight.W_600,
                    ),
                    ft.Text(
                        "0.4 points per minute of focus time",
                        size=CAPTION_FONT_SIZE,
                        color=TEXT_SECONDARY,
                    ),
                ],
            ),
        )

        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=PADDING_LG),
                    content=ft.Text(
                        "Settings",
                        size=TITLE_FONT_SIZE,
                        color=TEXT_PRIMARY,
                        weight=ft.FontWeight.W_700,
                    ),
                ),
                ft.Container(height=PADDING_MD),
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=PADDING_LG),
                    content=focus_section,
                ),
                ft.Container(height=PADDING_MD),
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=PADDING_LG),
                    content=break_section,
                ),
                ft.Container(height=PADDING_MD),
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=PADDING_LG),
                    content=rules_section,
                ),
            ],
        )

    def build(self, page: ft.Page) -> ft.Container:
        """Build the settings view."""
        self._page = page
        self._container = ft.Container(
            expand=True,
            bgcolor=BG_COLOR,
            padding=ft.Padding.only(top=PADDING_XL, bottom=PADDING_LG),
            content=self._build_content(),
        )
        return self._container
