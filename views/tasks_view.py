"""Tasks view — inline input with templates, difficulty selector, and sorted task list."""

import flet as ft

from theme import (
    BG_COLOR,
    SURFACE_COLOR,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TOMATO_RED,
    TOMATO_RED_DIM,
    TITLE_FONT_SIZE,
    SUBTITLE_FONT_SIZE,
    BODY_FONT_SIZE,
    CAPTION_FONT_SIZE,
    PADDING_SM,
    PADDING_MD,
    PADDING_LG,
    PADDING_XL,
    DIVIDER_COLOR,
)
from task_engine import (
    TaskManager,
    Task,
    Difficulty,
    SortMode,
    DIFFICULTY_LABELS,
    SORT_MODE_LABELS,
)
import storage

DIFFICULTY_COLORS = {
    Difficulty.VERY_EASY: "#4CAF50",
    Difficulty.EASY: "#8BC34A",
    Difficulty.NORMAL: "#FFC107",
    Difficulty.HARD: "#FF9800",
    Difficulty.VERY_HARD: "#F44336",
}

TEMPLATES = [
    ("Math Homework", Difficulty.NORMAL, 25),
    ("Chinese Essay", Difficulty.HARD, 45),
    ("English Reading", Difficulty.EASY, 20),
    ("Science Lab Report", Difficulty.HARD, 30),
    ("History Notes", Difficulty.NORMAL, 25),
    ("PE Exercise", Difficulty.VERY_EASY, 15),
    ("Music Practice", Difficulty.EASY, 20),
    ("Art Project", Difficulty.NORMAL, 30),
    ("Exam Review", Difficulty.VERY_HARD, 45),
    ("Reading 30min", Difficulty.EASY, 30),
]

DURATION_OPTIONS = [5, 10, 15, 20, 25, 30, 45, 60]


class TasksView:
    def __init__(self, task_manager: TaskManager, on_task_selected=None):
        self.tasks = task_manager
        self.on_task_selected = on_task_selected
        self._page: ft.Page | None = None
        self._container: ft.Container | None = None
        self._selected_difficulty = Difficulty.NORMAL
        self._selected_duration = 25

    def _save(self):
        storage.save_tasks(self.tasks.to_dict())

    def rebuild(self):
        if self._page and self._container:
            self._container.content = self._build_content()
            self._page.update()

    def _on_add_task(self, name_field: ft.TextField):
        name = name_field.value.strip() if name_field.value else ""
        if name:
            self.tasks.add_task(name, self._selected_difficulty, self._selected_duration)
            self._save()
            name_field.value = ""
            self.rebuild()

    def _on_add_template(self, name: str, difficulty: Difficulty, duration: int):
        self.tasks.add_task(name, difficulty, duration)
        self._save()
        self.rebuild()

    def _on_select_difficulty(self, diff: Difficulty):
        self._selected_difficulty = diff
        self.rebuild()

    def _on_select_duration(self, minutes: int):
        self._selected_duration = minutes
        self.rebuild()

    def _on_custom_duration(self, value: str):
        """Handle custom duration input — accept any positive number."""
        try:
            mins = int(value.strip())
            if mins > 0:
                self._selected_duration = mins
                self.rebuild()
        except (ValueError, TypeError):
            pass

    def _on_delete_task(self, task_id: str):
        self.tasks.remove_task(task_id)
        self._save()
        self.rebuild()

    def _on_toggle_done(self, task_id: str):
        self.tasks.toggle_done(task_id)
        self._save()
        self.rebuild()

    def _on_select_task(self, task: Task):
        if self.on_task_selected:
            self.on_task_selected(task)

    def _on_move_up(self, task_id: str):
        for i, t in enumerate(self.tasks.tasks):
            if t.id == task_id and i > 0:
                self.tasks.move_task(task_id, i - 1)
                break
        self._save()
        self.rebuild()

    def _on_move_down(self, task_id: str):
        for i, t in enumerate(self.tasks.tasks):
            if t.id == task_id and i < len(self.tasks.tasks) - 1:
                self.tasks.move_task(task_id, i + 1)
                break
        self._save()
        self.rebuild()

    def _on_sort_mode_changed(self, mode: SortMode):
        self.tasks.sort_mode = mode
        self._save()
        self.rebuild()

    def _build_sort_selector(self) -> ft.Row:
        chips = []
        for mode in SortMode:
            is_sel = mode == self.tasks.sort_mode
            chip = ft.Container(
                bgcolor=TOMATO_RED if is_sel else SURFACE_COLOR,
                border_radius=16,
                padding=ft.Padding.symmetric(horizontal=12, vertical=6),
                on_click=lambda _, m=mode: self._on_sort_mode_changed(m),
                content=ft.Text(
                    SORT_MODE_LABELS[mode],
                    size=CAPTION_FONT_SIZE,
                    color=TEXT_PRIMARY,
                    weight=ft.FontWeight.W_600 if is_sel else ft.FontWeight.W_400,
                ),
            )
            chips.append(chip)
        return ft.Row(spacing=8, controls=chips)

    def _build_task_card(self, task: Task, index: int, total: int) -> ft.Container:
        diff_color = DIFFICULTY_COLORS[task.difficulty]
        is_manual = self.tasks.sort_mode == SortMode.MANUAL

        left_controls = [
            ft.Checkbox(
                value=task.done,
                active_color=TOMATO_RED,
                on_change=lambda _, tid=task.id: self._on_toggle_done(tid),
            ),
            ft.Container(bgcolor=diff_color, border_radius=8, width=4, height=32),
            ft.Column(
                spacing=2,
                expand=True,
                controls=[
                    ft.Text(
                        task.name,
                        size=BODY_FONT_SIZE,
                        color=TEXT_SECONDARY if task.done else TEXT_PRIMARY,
                        style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH) if task.done else None,
                    ),
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.Text(
                                DIFFICULTY_LABELS[task.difficulty],
                                size=CAPTION_FONT_SIZE,
                                color=diff_color,
                            ),
                            ft.Text(
                                f"{task.duration_minutes}min",
                                size=CAPTION_FONT_SIZE,
                                color=TEXT_SECONDARY,
                            ),
                        ],
                    ),
                ],
            ),
        ]

        right_controls = []
        if is_manual and not task.done:
            if index > 0:
                right_controls.append(ft.IconButton(
                    icon=ft.Icons.ARROW_UPWARD, icon_color=TEXT_SECONDARY, icon_size=18,
                    on_click=lambda _, tid=task.id: self._on_move_up(tid),
                ))
            if index < total - 1:
                right_controls.append(ft.IconButton(
                    icon=ft.Icons.ARROW_DOWNWARD, icon_color=TEXT_SECONDARY, icon_size=18,
                    on_click=lambda _, tid=task.id: self._on_move_down(tid),
                ))

        if not task.done:
            right_controls.append(ft.IconButton(
                icon=ft.Icons.PLAY_CIRCLE_OUTLINE, icon_color=TOMATO_RED, icon_size=24,
                on_click=lambda _, t=task: self._on_select_task(t),
            ))

        right_controls.append(ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE, icon_color=TEXT_SECONDARY, icon_size=18,
            on_click=lambda _, tid=task.id: self._on_delete_task(tid),
        ))

        return ft.Container(
            bgcolor=SURFACE_COLOR,
            border_radius=12,
            padding=ft.Padding.symmetric(horizontal=PADDING_SM, vertical=PADDING_SM),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(expand=True, spacing=8,
                           vertical_alignment=ft.CrossAxisAlignment.CENTER,
                           controls=left_controls),
                    ft.Row(spacing=0, controls=right_controls),
                ],
            ),
        )

    def _build_input_area(self) -> ft.Container:
        """Chat-style input area at the bottom: templates + difficulty + text field + add button."""

        # Templates row
        template_chips = []
        for name, diff, dur in TEMPLATES:
            color = DIFFICULTY_COLORS[diff]
            chip = ft.Container(
                bgcolor=SURFACE_COLOR,
                border=ft.border.all(1, color),
                border_radius=16,
                padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                on_click=lambda _, n=name, d=diff, du=dur: self._on_add_template(n, d, du),
                content=ft.Text(f"{name} ({dur}m)", size=CAPTION_FONT_SIZE - 1, color=color),
            )
            template_chips.append(chip)

        templates_row = ft.Row(
            wrap=True,
            spacing=6,
            run_spacing=6,
            controls=template_chips,
        )

        # Difficulty selector
        diff_chips = []
        for diff in Difficulty:
            is_sel = diff == self._selected_difficulty
            color = DIFFICULTY_COLORS[diff]
            chip = ft.Container(
                bgcolor=color if is_sel else SURFACE_COLOR,
                border_radius=12,
                padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                on_click=lambda _, d=diff: self._on_select_difficulty(d),
                content=ft.Text(
                    DIFFICULTY_LABELS[diff],
                    size=CAPTION_FONT_SIZE - 1,
                    color=TEXT_PRIMARY if is_sel else TEXT_SECONDARY,
                ),
            )
            diff_chips.append(chip)

        diff_row = ft.Row(spacing=4, controls=diff_chips)

        # Duration selector: presets + custom input
        dur_chips = []
        for mins in DURATION_OPTIONS:
            is_sel = mins == self._selected_duration
            chip = ft.Container(
                bgcolor=TOMATO_RED if is_sel else SURFACE_COLOR,
                border_radius=12,
                padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                on_click=lambda _, m=mins: self._on_select_duration(m),
                content=ft.Text(
                    f"{mins}m",
                    size=CAPTION_FONT_SIZE - 1,
                    color=TEXT_PRIMARY if is_sel else TEXT_SECONDARY,
                ),
            )
            dur_chips.append(chip)

        # Custom duration input
        is_custom = self._selected_duration not in DURATION_OPTIONS
        custom_field = ft.TextField(
            value=str(self._selected_duration) if is_custom else "",
            hint_text="Custom",
            width=60,
            height=28,
            content_padding=ft.Padding.symmetric(horizontal=6, vertical=2),
            text_size=CAPTION_FONT_SIZE,
            color=TEXT_PRIMARY,
            hint_style=ft.TextStyle(color=TEXT_SECONDARY),
            bgcolor=TOMATO_RED_DIM if is_custom else SURFACE_COLOR,
            border_color=TOMATO_RED if is_custom else DIVIDER_COLOR,
            border_radius=12,
            on_submit=lambda e: self._on_custom_duration(e.control.value),
        )
        dur_chips.append(custom_field)
        dur_row = ft.Row(spacing=4, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=dur_chips)

        # Text field + add button
        name_field = ft.TextField(
            hint_text="Type a task...",
            bgcolor=SURFACE_COLOR,
            color=TEXT_PRIMARY,
            hint_style=ft.TextStyle(color=TEXT_SECONDARY),
            border_color=DIVIDER_COLOR,
            focused_border_color=TOMATO_RED,
            border_radius=12,
            content_padding=ft.Padding.symmetric(horizontal=12, vertical=10),
            expand=True,
            on_submit=lambda e: self._on_add_task(e.control),
        )

        add_btn = ft.IconButton(
            icon=ft.Icons.SEND_ROUNDED,
            icon_color=TOMATO_RED,
            icon_size=28,
            on_click=lambda _: self._on_add_task(name_field),
        )

        input_row = ft.Row(
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[name_field, add_btn],
        )

        return ft.Container(
            bgcolor=BG_COLOR,
            padding=ft.Padding.symmetric(horizontal=PADDING_LG, vertical=PADDING_SM),
            border=ft.border.only(top=ft.BorderSide(1, DIVIDER_COLOR)),
            content=ft.Column(
                spacing=6,
                tight=True,
                controls=[
                    ft.Text("Templates", size=CAPTION_FONT_SIZE, color=TEXT_SECONDARY),
                    templates_row,
                    ft.Container(height=2),
                    ft.Text("Difficulty", size=CAPTION_FONT_SIZE, color=TEXT_SECONDARY),
                    diff_row,
                    ft.Text("Duration", size=CAPTION_FONT_SIZE, color=TEXT_SECONDARY),
                    dur_row,
                    input_row,
                ],
            ),
        )

    def _build_content(self) -> ft.Column:
        sorted_tasks = self.tasks.get_sorted_tasks()
        pending_count = self.tasks.pending_count()
        pending_total = sum(1 for t in sorted_tasks if not t.done)

        header = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text("Tasks", size=TITLE_FONT_SIZE, color=TEXT_PRIMARY, weight=ft.FontWeight.W_700),
                ft.Text(
                    f"{pending_count} pending",
                    size=CAPTION_FONT_SIZE,
                    color=TEXT_SECONDARY,
                ),
            ],
        )

        sort_row = self._build_sort_selector()

        if not sorted_tasks:
            task_list = ft.Container(
                padding=PADDING_XL,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                    controls=[
                        ft.Text("No tasks yet", size=BODY_FONT_SIZE, color=TEXT_SECONDARY),
                        ft.Text("Type below or pick a template", size=CAPTION_FONT_SIZE, color=TEXT_SECONDARY),
                    ],
                ),
            )
        else:
            cards = []
            pending_idx = 0
            for task in sorted_tasks:
                if not task.done:
                    cards.append(self._build_task_card(task, pending_idx, pending_total))
                    pending_idx += 1
                else:
                    cards.append(self._build_task_card(task, 0, 0))
            task_list = ft.Column(spacing=8, controls=cards)

        # Scrollable task list area
        list_area = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Container(padding=ft.Padding.symmetric(horizontal=PADDING_LG), content=header),
                ft.Container(padding=ft.Padding.symmetric(horizontal=PADDING_LG), content=sort_row),
                ft.Container(height=8),
                ft.Container(padding=ft.Padding.symmetric(horizontal=PADDING_LG), content=task_list),
            ],
        )

        # Bottom input area
        input_area = self._build_input_area()

        return ft.Column(
            expand=True,
            spacing=0,
            controls=[list_area, input_area],
        )

    def build(self, page: ft.Page) -> ft.Container:
        self._page = page
        self._container = ft.Container(
            expand=True,
            bgcolor=BG_COLOR,
            padding=ft.Padding.only(top=PADDING_XL),
            content=self._build_content(),
        )
        return self._container
