"""Tasks view — add tasks, set difficulty, sort, and pick what to work on."""

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


class TasksView:
    def __init__(self, task_manager: TaskManager, on_task_selected=None):
        self.tasks = task_manager
        self.on_task_selected = on_task_selected
        self._page: ft.Page | None = None
        self._container: ft.Container | None = None

    def _save(self):
        storage.save_tasks(self.tasks.to_dict())

    def rebuild(self):
        if self._page and self._container:
            self._container.content = self._build_content()
            self._page.update()

    def _on_add_task(self, e):
        name_field = ft.TextField(
            label="Task name",
            autofocus=True,
            bgcolor=SURFACE_COLOR,
            color=TEXT_PRIMARY,
            label_style=ft.TextStyle(color=TEXT_SECONDARY),
            border_color=DIVIDER_COLOR,
            focused_border_color=TOMATO_RED,
        )

        difficulty_value = [Difficulty.NORMAL]

        def make_chip(diff: Difficulty):
            is_sel = diff == difficulty_value[0]
            return ft.Container(
                bgcolor=DIFFICULTY_COLORS[diff] if is_sel else SURFACE_COLOR,
                border_radius=16,
                padding=ft.Padding.symmetric(horizontal=12, vertical=6),
                on_click=lambda _, d=diff: _select_diff(d),
                content=ft.Text(
                    DIFFICULTY_LABELS[diff],
                    size=CAPTION_FONT_SIZE,
                    color=TEXT_PRIMARY if is_sel else TEXT_SECONDARY,
                    weight=ft.FontWeight.W_600 if is_sel else ft.FontWeight.W_400,
                ),
            )

        def _select_diff(d):
            difficulty_value[0] = d
            diff_row.controls = [make_chip(diff) for diff in Difficulty]
            self._page.update()

        diff_row = ft.Row(
            wrap=True,
            spacing=6,
            controls=[make_chip(diff) for diff in Difficulty],
        )

        def _submit(e):
            name = name_field.value.strip()
            if name:
                self.tasks.add_task(name, difficulty_value[0])
                self._save()
                self._page.close(dlg)
                self.rebuild()

        dlg = ft.AlertDialog(
            title=ft.Text("New Task", color=TEXT_PRIMARY),
            bgcolor=BG_COLOR,
            content=ft.Column(
                tight=True,
                spacing=16,
                controls=[
                    name_field,
                    ft.Text("Difficulty", size=CAPTION_FONT_SIZE, color=TEXT_SECONDARY),
                    diff_row,
                ],
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._page.close(dlg)),
                ft.TextButton("Add", on_click=_submit, style=ft.ButtonStyle(color=TOMATO_RED)),
            ],
        )
        self._page.open(dlg)

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
            ft.Container(
                bgcolor=diff_color,
                border_radius=8,
                width=4,
                height=32,
            ),
            ft.Column(
                spacing=2,
                expand=True,
                controls=[
                    ft.Text(
                        task.name,
                        size=BODY_FONT_SIZE,
                        color=TEXT_SECONDARY if task.done else TEXT_PRIMARY,
                        decoration=ft.TextDecoration.LINE_THROUGH if task.done else None,
                    ),
                    ft.Text(
                        DIFFICULTY_LABELS[task.difficulty],
                        size=CAPTION_FONT_SIZE,
                        color=diff_color,
                    ),
                ],
            ),
        ]

        right_controls = []

        if is_manual and not task.done:
            if index > 0:
                right_controls.append(ft.IconButton(
                    icon=ft.Icons.ARROW_UPWARD,
                    icon_color=TEXT_SECONDARY,
                    icon_size=18,
                    on_click=lambda _, tid=task.id: self._on_move_up(tid),
                ))
            if index < total - 1:
                right_controls.append(ft.IconButton(
                    icon=ft.Icons.ARROW_DOWNWARD,
                    icon_color=TEXT_SECONDARY,
                    icon_size=18,
                    on_click=lambda _, tid=task.id: self._on_move_down(tid),
                ))

        if not task.done:
            right_controls.append(ft.IconButton(
                icon=ft.Icons.PLAY_CIRCLE_OUTLINE,
                icon_color=TOMATO_RED,
                icon_size=24,
                tooltip="Start this task",
                on_click=lambda _, t=task: self._on_select_task(t),
            ))

        right_controls.append(ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            icon_color=TEXT_SECONDARY,
            icon_size=18,
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
                    ft.Row(
                        expand=True,
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=left_controls,
                    ),
                    ft.Row(spacing=0, controls=right_controls),
                ],
            ),
        )

    def _build_content(self) -> ft.Column:
        sorted_tasks = self.tasks.get_sorted_tasks()
        pending_count = self.tasks.pending_count()
        pending_total = sum(1 for t in sorted_tasks if not t.done)

        # Header
        header = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text(
                    "Tasks",
                    size=TITLE_FONT_SIZE,
                    color=TEXT_PRIMARY,
                    weight=ft.FontWeight.W_700,
                ),
                ft.IconButton(
                    icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                    icon_color=TOMATO_RED,
                    icon_size=28,
                    on_click=self._on_add_task,
                    tooltip="Add task",
                ),
            ],
        )

        # Sort selector
        sort_row = self._build_sort_selector()

        # Task count
        count_text = ft.Text(
            f"{pending_count} task{'s' if pending_count != 1 else ''} pending",
            size=CAPTION_FONT_SIZE,
            color=TEXT_SECONDARY,
        )

        # Task list
        if not sorted_tasks:
            task_list = ft.Container(
                padding=PADDING_XL,
                content=ft.Text(
                    "No tasks yet. Tap + to add one!",
                    size=BODY_FONT_SIZE,
                    color=TEXT_SECONDARY,
                    text_align=ft.TextAlign.CENTER,
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

        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=PADDING_LG),
                    content=header,
                ),
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=PADDING_LG),
                    content=sort_row,
                ),
                ft.Container(height=8),
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=PADDING_LG),
                    content=count_text,
                ),
                ft.Container(height=8),
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=PADDING_LG),
                    content=task_list,
                ),
            ],
        )

    def build(self, page: ft.Page) -> ft.Container:
        self._page = page
        self._container = ft.Container(
            expand=True,
            bgcolor=BG_COLOR,
            padding=ft.Padding.only(top=PADDING_XL, bottom=PADDING_LG),
            content=self._build_content(),
        )
        return self._container
