"""Settings view — warm linen design with theme cards, duration controls, and options."""

import flet as ft
import theme
from theme import (
    BODY_FONT_SIZE, CAPTION_FONT_SIZE, PADDING_LG, PADDING_MD, PADDING_XL,
    SUBTITLE_FONT_SIZE, PAGE_TITLE_SIZE, PADDING_SM,
)

import storage

# Available duration options
FOCUS_OPTIONS = [15, 20, 25, 30, 45, 60]
BREAK_OPTIONS = [3, 5, 10, 15]

# Theme card definitions (visual only — no runtime switching)
THEME_CARDS = [
    {
        "name": "Lakeside",
        "desc": "Calm blue-green lake",
        "swatches": ["#E8F4F0", "#4DACB0", "#2D3B36", "#B8DFE0"],
    },
    {
        "name": "Meadow",
        "desc": "Warm sunshine on grass",
        "swatches": ["#F0F7E8", "#6BBF59", "#2E3A28", "#C2E8B8"],
    },
    {
        "name": "Dusk",
        "desc": "Warm linen & moss",
        "swatches": ["#EFE9D9", "#2F5A3A", "#1F2A21", "#A8C49A"],
    },
]

# End sound options (visual only)
SOUND_OPTIONS = ["Chime", "Bowl", "Birds", "Silent"]


class SettingsView:
    """Settings screen with theme cards, duration selectors, and option toggles."""

    def __init__(self, on_settings_changed=None, on_theme_changed=None):
        self.on_settings_changed = on_settings_changed
        self.on_theme_changed = on_theme_changed
        self._page: ft.Page | None = None
        self._container: ft.Container | None = None
        self._selected_theme = 2  # Dusk (current design) is active
        self._selected_sound = 0  # Chime default
        self._dnd_enabled = False

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

    def _on_theme_selected(self, index: int):
        self._selected_theme = index
        self._rebuild()

    def _on_sound_selected(self, index: int):
        self._selected_sound = index
        self._rebuild()

    def _on_dnd_toggled(self, e):
        self._dnd_enabled = not self._dnd_enabled
        self._rebuild()

    def _rebuild(self):
        if self._page and self._container:
            self._container.content = self._build_content()
            self._page.update()

    def _build_segmented_row(self, options, selected, on_change, unit="min") -> ft.Row:
        """Build a segmented control row."""
        chips = []
        for opt in options:
            is_selected = opt == selected
            chip = ft.Container(
                bgcolor=theme.TEXT_PRIMARY if is_selected else None,
                border=ft.border.all(1, theme.TEXT_PRIMARY if is_selected else theme.DIVIDER_COLOR),
                border_radius=12,
                padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                on_click=lambda e, v=opt: on_change(
                    type("Event", (), {"control": type("Ctrl", (), {"value": v})()})()
                ),
                content=ft.Text(
                    f"{opt}" if unit == "" else f"{opt} {unit}",
                    size=BODY_FONT_SIZE,
                    color=theme.SURFACE_COLOR if is_selected else theme.TEXT_SECONDARY,
                    weight=ft.FontWeight.W_600 if is_selected else ft.FontWeight.W_400,
                ),
            )
            chips.append(chip)
        return ft.Row(wrap=True, spacing=6, controls=chips)

    def _build_theme_card(self, card_data: dict, index: int) -> ft.Container:
        """Build a theme preview card with color swatches."""
        is_active = index == self._selected_theme

        # Color swatches
        swatch_row = ft.Row(
            spacing=4,
            controls=[
                ft.Container(
                    width=20,
                    height=20,
                    border_radius=10,
                    bgcolor=color,
                    border=ft.border.all(1, theme.DIVIDER_COLOR),
                )
                for color in card_data["swatches"]
            ],
        )

        content = ft.Column(
            spacing=6,
            controls=[
                swatch_row,
                ft.Text(
                    card_data["name"],
                    size=BODY_FONT_SIZE,
                    color=theme.TEXT_PRIMARY,
                    weight=ft.FontWeight.W_600,
                ),
                ft.Text(
                    card_data["desc"],
                    size=CAPTION_FONT_SIZE,
                    color=theme.TEXT_SECONDARY,
                ),
            ],
        )

        card = ft.Container(
            bgcolor=theme.SURFACE_COLOR,
            border=ft.border.all(2, theme.MOSS if is_active else theme.DIVIDER_COLOR),
            border_radius=14,
            padding=PADDING_MD,
            expand=True,
            on_click=lambda _, i=index: self._on_theme_selected(i),
            content=ft.Stack(
                controls=[
                    content,
                    # Checkmark badge for active
                    ft.Container(
                        right=0,
                        top=0,
                        visible=is_active,
                        content=ft.Container(
                            width=20,
                            height=20,
                            border_radius=10,
                            bgcolor=theme.MOSS,
                            alignment=ft.Alignment.CENTER,
                            content=ft.Icon(ft.Icons.CHECK_ROUNDED, color="#FFFFFF", size=12),
                        ),
                    ),
                ],
            ),
        )
        return card

    def _build_section(self, title: str, content: ft.Control) -> ft.Column:
        """Build a labeled section."""
        return ft.Column(
            spacing=PADDING_SM,
            controls=[
                ft.Text(
                    title,
                    size=CAPTION_FONT_SIZE,
                    color=theme.TEXT_SECONDARY,
                    weight=ft.FontWeight.W_600,
                ),
                content,
            ],
        )

    def _build_content(self) -> ft.Column:
        # Title + version
        title_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text(
                    "Settings",
                    size=PAGE_TITLE_SIZE,
                    color=theme.TEXT_PRIMARY,
                    weight=ft.FontWeight.W_700,
                ),
                ft.Text(
                    "v1.0",
                    size=CAPTION_FONT_SIZE,
                    color=theme.TEXT_SECONDARY,
                ),
            ],
        )

        # APPEARANCE: theme cards in grid
        theme_grid = ft.Row(
            spacing=PADDING_SM,
            controls=[
                self._build_theme_card(card, i)
                for i, card in enumerate(THEME_CARDS)
            ],
        )
        appearance_section = self._build_section("APPEARANCE", theme_grid)

        # Focus duration
        focus_row = self._build_segmented_row(FOCUS_OPTIONS, self.focus_minutes, self._on_focus_changed)
        focus_section = self._build_section("FOCUS DURATION", focus_row)

        # Break duration
        break_row = self._build_segmented_row(BREAK_OPTIONS, self.break_minutes, self._on_break_changed)
        break_section = self._build_section("BREAK DURATION", break_row)

        # End sound (visual only)
        sound_chips = []
        for i, name in enumerate(SOUND_OPTIONS):
            is_sel = i == self._selected_sound
            chip = ft.Container(
                bgcolor=theme.TEXT_PRIMARY if is_sel else None,
                border=ft.border.all(1, theme.TEXT_PRIMARY if is_sel else theme.DIVIDER_COLOR),
                border_radius=12,
                padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                on_click=lambda _, idx=i: self._on_sound_selected(idx),
                content=ft.Text(
                    name,
                    size=BODY_FONT_SIZE,
                    color=theme.SURFACE_COLOR if is_sel else theme.TEXT_SECONDARY,
                    weight=ft.FontWeight.W_600 if is_sel else ft.FontWeight.W_400,
                ),
            )
            sound_chips.append(chip)
        sound_row = ft.Row(spacing=6, controls=sound_chips)
        sound_section = self._build_section("END SOUND", sound_row)

        # DND toggle card
        dnd_card = ft.Container(
            bgcolor=theme.SURFACE_COLOR,
            border_radius=14,
            padding=ft.Padding.symmetric(horizontal=PADDING_LG, vertical=PADDING_MD),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(
                                "Do Not Disturb",
                                size=BODY_FONT_SIZE,
                                color=theme.TEXT_PRIMARY,
                                weight=ft.FontWeight.W_600,
                            ),
                            ft.Text(
                                "Silence notifications during focus",
                                size=CAPTION_FONT_SIZE,
                                color=theme.TEXT_SECONDARY,
                            ),
                        ],
                    ),
                    ft.Switch(
                        value=self._dnd_enabled,
                        active_color=theme.MOSS,
                        on_change=self._on_dnd_toggled,
                    ),
                ],
            ),
        )
        dnd_section = self._build_section("NOTIFICATIONS", dnd_card)

        # Points rules info
        points_per_session = max(1, round(self.focus_minutes * 0.4))
        rules_card = ft.Container(
            bgcolor=theme.SURFACE_COLOR,
            border_radius=14,
            padding=PADDING_LG,
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Text(
                        f"Complete a {self.focus_minutes}-minute session = {points_per_session} points",
                        size=BODY_FONT_SIZE,
                        color=theme.MOSS,
                        weight=ft.FontWeight.W_600,
                    ),
                    ft.Text(
                        "0.4 points per minute of focus time",
                        size=CAPTION_FONT_SIZE,
                        color=theme.TEXT_SECONDARY,
                    ),
                ],
            ),
        )
        rules_section = self._build_section("POINTS RULES", rules_card)

        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=PADDING_LG),
                    content=title_row,
                ),
                ft.Container(height=PADDING_LG),
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=PADDING_LG),
                    content=appearance_section,
                ),
                ft.Container(height=PADDING_LG),
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=PADDING_LG),
                    content=focus_section,
                ),
                ft.Container(height=PADDING_LG),
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=PADDING_LG),
                    content=break_section,
                ),
                ft.Container(height=PADDING_LG),
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=PADDING_LG),
                    content=sound_section,
                ),
                ft.Container(height=PADDING_LG),
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=PADDING_LG),
                    content=dnd_section,
                ),
                ft.Container(height=PADDING_LG),
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=PADDING_LG),
                    content=rules_section,
                ),
                ft.Container(height=PADDING_LG),
            ],
        )

    def build(self, page: ft.Page) -> ft.Container:
        """Build the settings view."""
        self._page = page
        self._container = ft.Container(
            expand=True,
            bgcolor=None,
            padding=ft.Padding.only(top=PADDING_XL, bottom=PADDING_LG),
            content=self._build_content(),
        )
        return self._container
