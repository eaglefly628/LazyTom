"""Full path coverage tests for TaskManager, Task, sorting, and serialization."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from task_engine import (
    Task,
    TaskManager,
    Difficulty,
    SortMode,
    DIFFICULTY_LABELS,
    SORT_MODE_LABELS,
)


class TestTask:
    def test_creation_defaults(self):
        t = Task(name="Homework")
        assert t.name == "Homework"
        assert t.difficulty == Difficulty.NORMAL
        assert t.done is False
        assert t.id is not None
        assert t.created_at is not None

    def test_creation_with_all_fields(self):
        t = Task(name="Math", difficulty=Difficulty.HARD, task_id="abc", done=True, order=3)
        assert t.name == "Math"
        assert t.difficulty == Difficulty.HARD
        assert t.id == "abc"
        assert t.done is True
        assert t.order == 3

    def test_to_dict(self):
        t = Task(name="Read", difficulty=Difficulty.EASY, task_id="x1")
        d = t.to_dict()
        assert d["name"] == "Read"
        assert d["difficulty"] == 2
        assert d["id"] == "x1"
        assert d["done"] is False

    def test_from_dict(self):
        d = {"name": "Write", "difficulty": 4, "id": "y2", "done": True, "order": 5, "created_at": "2025-01-01"}
        t = Task.from_dict(d)
        assert t.name == "Write"
        assert t.difficulty == Difficulty.HARD
        assert t.id == "y2"
        assert t.done is True

    def test_from_dict_defaults(self):
        d = {"name": "Simple"}
        t = Task.from_dict(d)
        assert t.difficulty == Difficulty.NORMAL
        assert t.done is False

    def test_round_trip(self):
        t1 = Task(name="Test", difficulty=Difficulty.VERY_HARD, task_id="rt1")
        t2 = Task.from_dict(t1.to_dict())
        assert t2.name == t1.name
        assert t2.difficulty == t1.difficulty
        assert t2.id == t1.id


class TestTaskManagerBasic:
    def test_initial_state(self):
        tm = TaskManager()
        assert tm.tasks == []
        assert tm.sort_mode == SortMode.EASY_FIRST

    def test_add_task(self):
        tm = TaskManager()
        t = tm.add_task("Do homework", Difficulty.HARD)
        assert len(tm.tasks) == 1
        assert t.name == "Do homework"
        assert t.difficulty == Difficulty.HARD

    def test_add_multiple(self):
        tm = TaskManager()
        tm.add_task("A")
        tm.add_task("B")
        tm.add_task("C")
        assert len(tm.tasks) == 3

    def test_remove_task(self):
        tm = TaskManager()
        t = tm.add_task("Remove me")
        tm.remove_task(t.id)
        assert len(tm.tasks) == 0

    def test_remove_nonexistent(self):
        tm = TaskManager()
        tm.add_task("Keep")
        tm.remove_task("nonexistent")
        assert len(tm.tasks) == 1

    def test_toggle_done(self):
        tm = TaskManager()
        t = tm.add_task("Toggle")
        assert t.done is False
        tm.toggle_done(t.id)
        assert t.done is True
        tm.toggle_done(t.id)
        assert t.done is False

    def test_update_task(self):
        tm = TaskManager()
        t = tm.add_task("Old name", Difficulty.EASY)
        tm.update_task(t.id, name="New name", difficulty=Difficulty.VERY_HARD)
        assert t.name == "New name"
        assert t.difficulty == Difficulty.VERY_HARD

    def test_update_partial(self):
        tm = TaskManager()
        t = tm.add_task("Name", Difficulty.EASY)
        tm.update_task(t.id, name="Changed")
        assert t.name == "Changed"
        assert t.difficulty == Difficulty.EASY

    def test_pending_count(self):
        tm = TaskManager()
        tm.add_task("A")
        tm.add_task("B")
        t = tm.add_task("C")
        tm.toggle_done(t.id)
        assert tm.pending_count() == 2


class TestSorting:
    def _make_manager(self):
        tm = TaskManager()
        tm.add_task("Very Hard", Difficulty.VERY_HARD)
        tm.add_task("Easy", Difficulty.EASY)
        tm.add_task("Normal", Difficulty.NORMAL)
        tm.add_task("Very Easy", Difficulty.VERY_EASY)
        tm.add_task("Hard", Difficulty.HARD)
        return tm

    def test_easy_first(self):
        tm = self._make_manager()
        tm.sort_mode = SortMode.EASY_FIRST
        names = [t.name for t in tm.get_sorted_tasks()]
        assert names == ["Very Easy", "Easy", "Normal", "Hard", "Very Hard"]

    def test_hard_first(self):
        tm = self._make_manager()
        tm.sort_mode = SortMode.HARD_FIRST
        names = [t.name for t in tm.get_sorted_tasks()]
        assert names == ["Very Hard", "Hard", "Normal", "Easy", "Very Easy"]

    def test_manual_preserves_insertion_order(self):
        tm = self._make_manager()
        tm.sort_mode = SortMode.MANUAL
        names = [t.name for t in tm.get_sorted_tasks()]
        assert names == ["Very Hard", "Easy", "Normal", "Very Easy", "Hard"]

    def test_done_tasks_go_to_bottom(self):
        tm = TaskManager()
        t1 = tm.add_task("A", Difficulty.EASY)
        tm.add_task("B", Difficulty.HARD)
        tm.add_task("C", Difficulty.NORMAL)
        tm.toggle_done(t1.id)
        tm.sort_mode = SortMode.EASY_FIRST
        sorted_tasks = tm.get_sorted_tasks()
        assert sorted_tasks[-1].name == "A"
        assert sorted_tasks[-1].done is True

    def test_get_next_task_easy_first(self):
        tm = self._make_manager()
        tm.sort_mode = SortMode.EASY_FIRST
        assert tm.get_next_task().name == "Very Easy"

    def test_get_next_task_hard_first(self):
        tm = self._make_manager()
        tm.sort_mode = SortMode.HARD_FIRST
        assert tm.get_next_task().name == "Very Hard"

    def test_get_next_task_all_done(self):
        tm = TaskManager()
        t = tm.add_task("Only task")
        tm.toggle_done(t.id)
        assert tm.get_next_task() is None

    def test_get_next_task_empty(self):
        tm = TaskManager()
        assert tm.get_next_task() is None

    def test_same_difficulty_preserves_order(self):
        tm = TaskManager()
        tm.add_task("First", Difficulty.NORMAL)
        tm.add_task("Second", Difficulty.NORMAL)
        tm.add_task("Third", Difficulty.NORMAL)
        tm.sort_mode = SortMode.EASY_FIRST
        names = [t.name for t in tm.get_sorted_tasks()]
        assert names == ["First", "Second", "Third"]


class TestMoveTask:
    def test_move_up(self):
        tm = TaskManager()
        tm.add_task("A")
        t = tm.add_task("B")
        tm.add_task("C")
        tm.sort_mode = SortMode.MANUAL
        tm.move_task(t.id, 0)
        names = [t.name for t in tm.get_sorted_tasks()]
        assert names == ["B", "A", "C"]

    def test_move_down(self):
        tm = TaskManager()
        t = tm.add_task("A")
        tm.add_task("B")
        tm.add_task("C")
        tm.sort_mode = SortMode.MANUAL
        tm.move_task(t.id, 2)
        names = [t.name for t in tm.get_sorted_tasks()]
        assert names == ["B", "C", "A"]

    def test_move_to_same(self):
        tm = TaskManager()
        t = tm.add_task("A")
        tm.add_task("B")
        tm.sort_mode = SortMode.MANUAL
        tm.move_task(t.id, 0)
        assert [t.name for t in tm.get_sorted_tasks()] == ["A", "B"]

    def test_move_nonexistent(self):
        tm = TaskManager()
        tm.add_task("A")
        tm.move_task("nope", 0)
        assert len(tm.tasks) == 1

    def test_move_clamps_index(self):
        tm = TaskManager()
        t = tm.add_task("A")
        tm.add_task("B")
        tm.move_task(t.id, 999)
        assert tm.tasks[-1].name == "A"

    def test_order_updated_after_move(self):
        tm = TaskManager()
        tm.add_task("A")
        t = tm.add_task("B")
        tm.add_task("C")
        tm.move_task(t.id, 0)
        for i, task in enumerate(tm.tasks):
            assert task.order == i


class TestSerialization:
    def test_to_dict(self):
        tm = TaskManager()
        tm.add_task("A", Difficulty.EASY)
        tm.add_task("B", Difficulty.HARD)
        tm.sort_mode = SortMode.HARD_FIRST
        d = tm.to_dict()
        assert len(d["tasks"]) == 2
        assert d["sort_mode"] == 2

    def test_load_from_dict(self):
        data = {
            "tasks": [
                {"name": "X", "difficulty": 1, "id": "a1", "done": False, "order": 0},
                {"name": "Y", "difficulty": 5, "id": "a2", "done": True, "order": 1},
            ],
            "sort_mode": 3,
        }
        tm = TaskManager()
        tm.load_from_dict(data)
        assert len(tm.tasks) == 2
        assert tm.tasks[0].name == "X"
        assert tm.tasks[1].done is True
        assert tm.sort_mode == SortMode.MANUAL

    def test_load_empty(self):
        tm = TaskManager()
        tm.load_from_dict({})
        assert tm.tasks == []
        assert tm.sort_mode == SortMode.EASY_FIRST

    def test_round_trip(self):
        tm1 = TaskManager()
        tm1.add_task("A", Difficulty.VERY_EASY)
        tm1.add_task("B", Difficulty.VERY_HARD)
        tm1.sort_mode = SortMode.HARD_FIRST
        tm1.toggle_done(tm1.tasks[0].id)

        tm2 = TaskManager()
        tm2.load_from_dict(tm1.to_dict())
        assert len(tm2.tasks) == 2
        assert tm2.tasks[0].done is True
        assert tm2.sort_mode == SortMode.HARD_FIRST


class TestLabels:
    def test_difficulty_labels(self):
        assert len(DIFFICULTY_LABELS) == 5
        assert DIFFICULTY_LABELS[Difficulty.VERY_EASY] == "Very Easy"
        assert DIFFICULTY_LABELS[Difficulty.VERY_HARD] == "Very Hard"

    def test_sort_mode_labels(self):
        assert len(SORT_MODE_LABELS) == 3
        assert SORT_MODE_LABELS[SortMode.EASY_FIRST] == "Easy First"
