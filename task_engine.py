"""Task management engine — task model, sorting strategies, persistence."""

from enum import IntEnum
from datetime import datetime
import uuid


class Difficulty(IntEnum):
    VERY_EASY = 1
    EASY = 2
    NORMAL = 3
    HARD = 4
    VERY_HARD = 5


DIFFICULTY_LABELS = {
    Difficulty.VERY_EASY: "Very Easy",
    Difficulty.EASY: "Easy",
    Difficulty.NORMAL: "Normal",
    Difficulty.HARD: "Hard",
    Difficulty.VERY_HARD: "Very Hard",
}


class SortMode(IntEnum):
    EASY_FIRST = 1
    HARD_FIRST = 2
    MANUAL = 3


SORT_MODE_LABELS = {
    SortMode.EASY_FIRST: "Easy First",
    SortMode.HARD_FIRST: "Hard First",
    SortMode.MANUAL: "Manual",
}


class Task:
    def __init__(
        self,
        name: str,
        difficulty: Difficulty = Difficulty.NORMAL,
        duration_minutes: int = 25,
        task_id: str | None = None,
        done: bool = False,
        order: int = 0,
        created_at: str | None = None,
    ):
        self.id = task_id or uuid.uuid4().hex[:8]
        self.name = name
        self.difficulty = difficulty
        self.duration_minutes = duration_minutes
        self.done = done
        self.order = order
        self.created_at = created_at or datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "difficulty": int(self.difficulty),
            "duration_minutes": self.duration_minutes,
            "done": self.done,
            "order": self.order,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            name=data["name"],
            difficulty=Difficulty(data.get("difficulty", 3)),
            duration_minutes=data.get("duration_minutes", 25),
            task_id=data.get("id"),
            done=data.get("done", False),
            order=data.get("order", 0),
            created_at=data.get("created_at"),
        )


class TaskManager:
    def __init__(self):
        self.tasks: list[Task] = []
        self.sort_mode: SortMode = SortMode.EASY_FIRST

    def add_task(self, name: str, difficulty: Difficulty = Difficulty.NORMAL, duration_minutes: int = 25) -> Task:
        task = Task(name=name, difficulty=difficulty, duration_minutes=duration_minutes, order=len(self.tasks))
        self.tasks.append(task)
        return task

    def remove_task(self, task_id: str):
        self.tasks = [t for t in self.tasks if t.id != task_id]

    def toggle_done(self, task_id: str):
        for t in self.tasks:
            if t.id == task_id:
                t.done = not t.done
                break

    def update_task(self, task_id: str, name: str | None = None, difficulty: Difficulty | None = None):
        for t in self.tasks:
            if t.id == task_id:
                if name is not None:
                    t.name = name
                if difficulty is not None:
                    t.difficulty = difficulty
                break

    def move_task(self, task_id: str, new_index: int):
        """Move a task to a new position (for manual sort)."""
        task = None
        for t in self.tasks:
            if t.id == task_id:
                task = t
                break
        if task is None:
            return
        self.tasks.remove(task)
        new_index = max(0, min(new_index, len(self.tasks)))
        self.tasks.insert(new_index, task)
        for i, t in enumerate(self.tasks):
            t.order = i

    def get_sorted_tasks(self) -> list[Task]:
        """Return tasks sorted by current sort mode. Done tasks go to bottom."""
        pending = [t for t in self.tasks if not t.done]
        done = [t for t in self.tasks if t.done]

        if self.sort_mode == SortMode.EASY_FIRST:
            pending.sort(key=lambda t: (t.difficulty, t.order))
        elif self.sort_mode == SortMode.HARD_FIRST:
            pending.sort(key=lambda t: (-t.difficulty, t.order))
        else:
            pending.sort(key=lambda t: t.order)

        return pending + done

    def get_next_task(self) -> Task | None:
        """Get the top undone task based on current sort."""
        sorted_tasks = self.get_sorted_tasks()
        for t in sorted_tasks:
            if not t.done:
                return t
        return None

    def pending_count(self) -> int:
        return sum(1 for t in self.tasks if not t.done)

    def to_dict(self) -> dict:
        return {
            "tasks": [t.to_dict() for t in self.tasks],
            "sort_mode": int(self.sort_mode),
        }

    def load_from_dict(self, data: dict):
        self.tasks = [Task.from_dict(d) for d in data.get("tasks", [])]
        self.sort_mode = SortMode(data.get("sort_mode", 1))
