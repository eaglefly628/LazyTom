"""Tasks view — warm linen design with hero card, flat task list, and composer."""

import flet as ft

import theme
from theme import (
    PAGE_TITLE_SIZE, SUBTITLE_FONT_SIZE, BODY_FONT_SIZE, CAPTION_FONT_SIZE,
    PADDING_SM, PADDING_MD, PADDING_LG, PADDING_XL,
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
from mood_engine import MoodManager, MoodLevel, MOOD_LABELS
from components.mood_picker import show_mood_picker

DIFFICULTY_COLORS = {
    Difficulty.VERY_EASY: '#7AA2C2',   # sky
    Difficulty.EASY: '#A8C49A',         # leaf
    Difficulty.NORMAL: '#5C8A5C',       # mossSoft
    Difficulty.HARD: '#D9A24E',         # amber
    Difficulty.VERY_HARD: '#B85A5A',    # rose
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


def _points_for_task(task: Task) -> int:
    """Estimate points a task would earn."""
    return max(1, round(task.duration_minutes * 0.4))


class TasksView:
    def __init__(self, task_manager: TaskManager, mood_manager: MoodManager | None = None, on_task_selected=None):
        self.tasks = task_manager
        self.mood = mood_manager or MoodManager()
        self.on_task_selected = on_task_selected
        self._page: ft.Page | None = None
        self._container: ft.Container | None = None
        self._selected_difficulty = Difficulty.NORMAL
        self._selected_duration = 25
        self._mood_sort_active = False
        self._mood_sort_mood: MoodLevel | None = None

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
        """Handle custom duration input."""
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

    def _build_sort_selector(self) -> ft.Container:
        """Build segmented sort control: ORDER label + 3-option pill."""
        chips = []
        for mode in SortMode:
            is_sel = mode == self.tasks.sort_mode
            chip = ft.Container(
                bgcolor=theme.TEXT_PRIMARY if is_sel else None,
                border_radius=12,
                padding=ft.Padding.symmetric(horizontal=12, vertical=6),
                on_click=lambda _, m=mode: self._on_sort_mode_changed(m),
                content=ft.Text(
                    SORT_MODE_LABELS[mode],
                    size=CAPTION_FONT_SIZE,
                    color=theme.SURFACE_COLOR if is_sel else theme.TEXT_SECONDARY,
                    weight=ft.FontWeight.W_600 if is_sel else ft.FontWeight.W_400,
                ),
            )
            chips.append(chip)

        pill = ft.Container(
            bgcolor=theme.SURFACE_COLOR,
            border_radius=14,
            border=ft.border.all(1, theme.DIVIDER_COLOR),
            padding=ft.Padding.symmetric(horizontal=2, vertical=2),
            content=ft.Row(spacing=0, controls=chips),
        )

        return ft.Row(
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    "ORDER",
                    size=CAPTION_FONT_SIZE,
                    color=theme.TEXT_SECONDARY,
                    weight=ft.FontWeight.W_600,
                ),
                pill,
            ],
        )

    def _build_hero_card(self, task: Task) -> ft.Container:
        """Build the 'Start with this' hero card for the top undone task."""
        diff_color = DIFFICULTY_COLORS[task.difficulty]
        pts = _points_for_task(task)

        return ft.Container(
            bgcolor=theme.SURFACE_COLOR,
            border=ft.border.all(1, theme.LINE_STRONG),
            border_radius=16,
            padding=PADDING_LG,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(
                        spacing=8,
                        expand=True,
                        controls=[
                            ft.Row(
                                spacing=6,
                                controls=[
                                    ft.Icon(ft.Icons.WB_SUNNY_OUTLINED, color=theme.CLAY, size=16),
                                    ft.Text(
                                        "START WITH THIS",
                                        size=CAPTION_FONT_SIZE,
                                        color=theme.CLAY,
                                        weight=ft.FontWeight.W_700,
                                    ),
                                ],
                            ),
                            ft.Text(
                                task.name,
                                size=SUBTITLE_FONT_SIZE,
                                color=theme.TEXT_PRIMARY,
                                weight=ft.FontWeight.W_700,
                            ),
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Container(
                                        bgcolor=diff_color,
                                        border_radius=8,
                                        padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                                        content=ft.Text(
                                            DIFFICULTY_LABELS[task.difficulty],
                                            size=CAPTION_FONT_SIZE,
                                            color="#FFFFFF",
                                            weight=ft.FontWeight.W_600,
                                        ),
                                    ),
                                    ft.Text(
                                        f"{task.duration_minutes} min · +{pts} pts",
                                        size=CAPTION_FONT_SIZE,
                                        color=theme.TEXT_SECONDARY,
                                    ),
                                ],
                            ),
                        ],
                    ),
                    # Big play button
                    ft.Container(
                        width=52,
                        height=52,
                        border_radius=26,
                        bgcolor=theme.MOSS,
                        alignment=ft.Alignment.CENTER,
                        on_click=lambda _, t=task: self._on_select_task(t),
                        content=ft.Icon(ft.Icons.PLAY_ARROW_ROUNDED, color=theme.CREAM, size=28),
                    ),
                ],
            ),
        )

    def _build_task_row(self, task: Task, index: int, total: int) -> ft.Container:
        """Build a flat task row with checkbox, difficulty dot, and play button."""
        diff_color = DIFFICULTY_COLORS[task.difficulty]
        is_manual = self.tasks.sort_mode == SortMode.MANUAL

        # Rounded square checkbox
        checkbox = ft.Container(
            width=22,
            height=22,
            border_radius=6,
            border=ft.border.all(2, theme.MOSS if task.done else theme.LINE_STRONG),
            bgcolor=theme.MOSS if task.done else None,
            alignment=ft.Alignment.CENTER,
            on_click=lambda _, tid=task.id: self._on_toggle_done(tid),
            content=ft.Icon(ft.Icons.CHECK_ROUNDED, color="#FFFFFF", size=14) if task.done else None,
        )

        # Task info
        task_info = ft.Row(
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
            controls=[
                checkbox,
                # Difficulty dot
                ft.Container(
                    width=6,
                    height=6,
                    border_radius=3,
                    bgcolor=diff_color,
                ),
                ft.Column(
                    spacing=0,
                    expand=True,
                    controls=[
                        ft.Text(
                            task.name,
                            size=BODY_FONT_SIZE,
                            color=theme.TEXT_SECONDARY if task.done else theme.TEXT_PRIMARY,
                            style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH) if task.done else None,
                        ),
                        ft.Text(
                            f"{DIFFICULTY_LABELS[task.difficulty]} · {task.duration_minutes}m",
                            size=CAPTION_FONT_SIZE,
                            color=theme.TEXT_SECONDARY,
                        ),
                    ],
                ),
            ],
        )

        right_controls = []

        if is_manual and not task.done:
            if index > 0:
                right_controls.append(ft.IconButton(
                    icon=ft.Icons.ARROW_UPWARD, icon_color=theme.TEXT_SECONDARY, icon_size=16,
                    on_click=lambda _, tid=task.id: self._on_move_up(tid),
                ))
            if index < total - 1:
                right_controls.append(ft.IconButton(
                    icon=ft.Icons.ARROW_DOWNWARD, icon_color=theme.TEXT_SECONDARY, icon_size=16,
                    on_click=lambda _, tid=task.id: self._on_move_down(tid),
                ))

        if not task.done:
            # Small round play button
            right_controls.append(
                ft.Container(
                    width=32,
                    height=32,
                    border_radius=16,
                    bgcolor=theme.MOSS,
                    alignment=ft.Alignment.CENTER,
                    on_click=lambda _, t=task: self._on_select_task(t),
                    content=ft.Icon(ft.Icons.PLAY_ARROW_ROUNDED, color=theme.CREAM, size=18),
                )
            )

        right_controls.append(ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE, icon_color=theme.TEXT_SECONDARY, icon_size=16,
            on_click=lambda _, tid=task.id: self._on_delete_task(tid),
        ))

        return ft.Container(
            padding=ft.Padding.symmetric(vertical=PADDING_SM),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(expand=True, content=task_info),
                    ft.Row(spacing=0, controls=right_controls),
                ],
            ),
        )

    def _build_input_area(self) -> ft.Container:
        """Composer card: templates, difficulty, duration, text input."""

        # Templates section with pill chips
        template_chips = []
        for name, diff, dur in TEMPLATES:
            color = DIFFICULTY_COLORS[diff]
            chip = ft.Container(
                bgcolor=theme.SURFACE_COLOR,
                border=ft.border.all(1, theme.DIVIDER_COLOR),
                border_radius=14,
                padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                on_click=lambda _, n=name, d=diff, du=dur: self._on_add_template(n, d, du),
                content=ft.Row(
                    spacing=4,
                    controls=[
                        ft.Container(width=5, height=5, border_radius=3, bgcolor=color),
                        ft.Text(
                            f"{name} · {dur}m",
                            size=CAPTION_FONT_SIZE,
                            color=theme.INK_SOFT,
                        ),
                    ],
                ),
            )
            template_chips.append(chip)

        templates_row = ft.Row(
            wrap=True,
            spacing=6,
            run_spacing=6,
            controls=template_chips,
        )

        # Difficulty row: 5 evenly-spaced buttons
        diff_chips = []
        for diff in Difficulty:
            is_sel = diff == self._selected_difficulty
            color = DIFFICULTY_COLORS[diff]
            chip = ft.Container(
                bgcolor=color if is_sel else None,
                border=ft.border.all(1, color if is_sel else theme.DIVIDER_COLOR),
                border_radius=10,
                padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                on_click=lambda _, d=diff: self._on_select_difficulty(d),
                expand=True,
                alignment=ft.Alignment.CENTER,
                content=ft.Text(
                    DIFFICULTY_LABELS[diff],
                    size=CAPTION_FONT_SIZE,
                    color="#FFFFFF" if is_sel else theme.TEXT_SECONDARY,
                    weight=ft.FontWeight.W_600 if is_sel else ft.FontWeight.W_400,
                    text_align=ft.TextAlign.CENTER,
                ),
            )
            diff_chips.append(chip)

        diff_row = ft.Row(spacing=4, controls=diff_chips)

        # Duration row: 8 buttons, active = dark ink fill
        dur_chips = []
        for mins in DURATION_OPTIONS:
            is_sel = mins == self._selected_duration
            chip = ft.Container(
                bgcolor=theme.TEXT_PRIMARY if is_sel else None,
                border=ft.border.all(1, theme.TEXT_PRIMARY if is_sel else theme.DIVIDER_COLOR),
                border_radius=10,
                padding=ft.Padding.symmetric(horizontal=6, vertical=4),
                on_click=lambda _, m=mins: self._on_select_duration(m),
                content=ft.Text(
                    f"{mins}m",
                    size=CAPTION_FONT_SIZE,
                    color=theme.SURFACE_COLOR if is_sel else theme.TEXT_SECONDARY,
                    weight=ft.FontWeight.W_600 if is_sel else ft.FontWeight.W_400,
                ),
            )
            dur_chips.append(chip)

        dur_row = ft.Row(spacing=4, controls=dur_chips)

        # Text field + moss send button
        name_field = ft.TextField(
            hint_text="Type a task...",
            bgcolor=theme.BG_COLOR,
            color=theme.TEXT_PRIMARY,
            hint_style=ft.TextStyle(color=theme.TEXT_SECONDARY),
            border_color=theme.DIVIDER_COLOR,
            focused_border_color=theme.MOSS,
            border_radius=12,
            content_padding=ft.Padding.symmetric(horizontal=12, vertical=10),
            expand=True,
            on_submit=lambda e: self._on_add_task(e.control),
        )

        send_btn = ft.Container(
            width=40,
            height=40,
            border_radius=12,
            bgcolor=theme.MOSS,
            alignment=ft.Alignment.CENTER,
            on_click=lambda _: self._on_add_task(name_field),
            content=ft.Icon(ft.Icons.SEND_ROUNDED, color=theme.CREAM, size=20),
        )

        input_row = ft.Row(
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[name_field, send_btn],
        )

        return ft.Container(
            bgcolor=theme.SURFACE_COLOR,
            border=ft.border.only(top=ft.BorderSide(1, theme.LINE_STRONG)),
            border_radius=ft.border_radius.only(top_left=16, top_right=16),
            padding=ft.Padding.symmetric(horizontal=PADDING_LG, vertical=PADDING_SM + 4),
            content=ft.Column(
                spacing=8,
                tight=True,
                controls=[
                    ft.Text("TEMPLATES", size=CAPTION_FONT_SIZE, color=theme.TEXT_SECONDARY, weight=ft.FontWeight.W_600),
                    templates_row,
                    ft.Container(height=2),
                    ft.Text("DIFFICULTY", size=CAPTION_FONT_SIZE, color=theme.TEXT_SECONDARY, weight=ft.FontWeight.W_600),
                    diff_row,
                    ft.Text("DURATION", size=CAPTION_FONT_SIZE, color=theme.TEXT_SECONDARY, weight=ft.FontWeight.W_600),
                    dur_row,
                    ft.Container(height=2),
                    input_row,
                ],
            ),
        )

    def _on_recommend_clicked(self, _=None):
        if self._page is None:
            return

        def _on_mood(mood: MoodLevel):
            self._mood_sort_active = True
            self._mood_sort_mood = mood
            self.mood.set_current_mood(mood)
            storage.save_mood(self.mood.to_dict())
            self.rebuild()

        show_mood_picker(self._page, "How are you feeling?", _on_mood)

    def _on_clear_mood_sort(self, _=None):
        self._mood_sort_active = False
        self._mood_sort_mood = None
        self.rebuild()

    def _build_content(self) -> ft.Column:
        if self._mood_sort_active and self._mood_sort_mood is not None:
            recommended = self.mood.recommend_tasks(self.tasks.tasks, self._mood_sort_mood)
            done_tasks = [t for t in self.tasks.tasks if t.done]
            sorted_tasks = recommended + done_tasks
        else:
            sorted_tasks = self.tasks.get_sorted_tasks()
        pending_count = self.tasks.pending_count()
        pending_total = sum(1 for t in sorted_tasks if not t.done)

        # Total pending duration
        total_minutes = sum(t.duration_minutes for t in sorted_tasks if not t.done)
        hours = total_minutes // 60
        mins = total_minutes % 60
        if hours > 0 and mins > 0:
            time_str = f"{hours}h {mins}m"
        elif hours > 0:
            time_str = f"{hours}h"
        else:
            time_str = f"{mins}m"

        # Header
        header = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    "Tasks",
                    size=PAGE_TITLE_SIZE,
                    color=theme.TEXT_PRIMARY,
                    weight=ft.FontWeight.W_700,
                ),
                ft.Row(
                    spacing=6,
                    controls=[
                        ft.Container(
                            width=8,
                            height=8,
                            border_radius=4,
                            bgcolor=theme.CLAY,
                        ),
                        ft.Text(
                            f"{pending_count} pending · {time_str}",
                            size=CAPTION_FONT_SIZE,
                            color=theme.INK_SOFT,
                        ),
                    ],
                ),
            ],
        )

        # Hero card for first undone task
        next_task = self.tasks.get_next_task()
        hero = None
        if next_task and not self._mood_sort_active:
            # Use the first task from sorted list
            for t in sorted_tasks:
                if not t.done:
                    hero = self._build_hero_card(t)
                    break

        # Sort selector
        sort_row = self._build_sort_selector()

        # Mood sort banner
        banner = None
        if self._mood_sort_active and self._mood_sort_mood is not None:
            banner = ft.Container(
                bgcolor=theme.SURFACE_COLOR,
                border_radius=10,
                padding=ft.Padding.symmetric(horizontal=PADDING_SM, vertical=6),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            f"Sorted by mood: {MOOD_LABELS[self._mood_sort_mood]}",
                            size=CAPTION_FONT_SIZE,
                            color=theme.TEXT_SECONDARY,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE_ROUNDED,
                            icon_color=theme.TEXT_SECONDARY,
                            icon_size=16,
                            on_click=self._on_clear_mood_sort,
                            tooltip="Clear mood sort",
                        ),
                    ],
                ),
            )

        # Task list (flat rows with dividers)
        if not sorted_tasks:
            task_list = ft.Container(
                padding=PADDING_XL,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                    controls=[
                        ft.Text("No tasks yet", size=BODY_FONT_SIZE, color=theme.TEXT_SECONDARY),
                        ft.Text("Type below or pick a template", size=CAPTION_FONT_SIZE, color=theme.TEXT_SECONDARY),
                    ],
                ),
            )
        else:
            rows = []
            pending_idx = 0
            hero_task_id = None
            # Find the hero task id to skip it in the list
            if hero:
                for t in sorted_tasks:
                    if not t.done:
                        hero_task_id = t.id
                        break

            for task in sorted_tasks:
                if task.id == hero_task_id:
                    continue  # Already shown in hero card
                if not task.done:
                    rows.append(self._build_task_row(task, pending_idx, pending_total))
                    # Divider between rows
                    rows.append(ft.Container(height=1, bgcolor=theme.DIVIDER_COLOR))
                    pending_idx += 1
                else:
                    rows.append(self._build_task_row(task, 0, 0))
                    rows.append(ft.Container(height=1, bgcolor=theme.DIVIDER_COLOR))

            # Remove trailing divider
            if rows and isinstance(rows[-1], ft.Container) and rows[-1].height == 1:
                rows.pop()

            task_list = ft.Column(spacing=0, controls=rows)

        # Build scrollable area
        list_controls = [
            ft.Container(padding=ft.Padding.symmetric(horizontal=PADDING_LG), content=header),
            ft.Container(height=PADDING_MD),
        ]

        if hero:
            list_controls.append(
                ft.Container(padding=ft.Padding.symmetric(horizontal=PADDING_LG), content=hero)
            )
            list_controls.append(ft.Container(height=PADDING_MD))

        if banner is not None:
            list_controls.append(
                ft.Container(padding=ft.Padding.symmetric(horizontal=PADDING_LG), content=banner)
            )
            list_controls.append(ft.Container(height=PADDING_SM))

        # Recommend button
        recommend_btn = ft.Container(
            border=ft.border.all(1, theme.LINE_STRONG),
            border_radius=12,
            padding=ft.Padding.symmetric(horizontal=PADDING_MD, vertical=PADDING_SM),
            ink=True,
            on_click=self._on_recommend_clicked,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=6,
                controls=[
                    ft.Icon(ft.Icons.AUTO_AWESOME, color=theme.CLAY, size=16),
                    ft.Text(
                        "Recommend for me",
                        size=BODY_FONT_SIZE,
                        color=theme.INK_SOFT,
                        weight=ft.FontWeight.W_600,
                    ),
                ],
            ),
        )
        list_controls.append(
            ft.Container(padding=ft.Padding.symmetric(horizontal=PADDING_LG), content=recommend_btn)
        )
        list_controls.append(ft.Container(height=PADDING_SM))

        list_controls.extend([
            ft.Container(padding=ft.Padding.symmetric(horizontal=PADDING_LG), content=sort_row),
            ft.Container(height=PADDING_SM),
            ft.Container(padding=ft.Padding.symmetric(horizontal=PADDING_LG), content=task_list),
        ])

        list_area = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=list_controls,
        )

        # Bottom composer
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
            bgcolor=None,
            padding=ft.Padding.only(top=PADDING_XL),
            content=self._build_content(),
        )
        return self._container
