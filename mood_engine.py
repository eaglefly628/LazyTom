"""Mood tracking & emotion-aware task recommendation engine.

Rule-based (non-AI) mood-to-difficulty mapping for Phase 1.
Runs entirely locally; no network calls.
"""

from enum import IntEnum
from datetime import datetime, date
import uuid

from task_engine import Task, Difficulty


class MoodLevel(IntEnum):
    EXHAUSTED = 1
    TIRED = 2
    NORMAL = 3
    ENERGETIC = 4


MOOD_LABELS = {
    MoodLevel.ENERGETIC: "💪 精力充沛",
    MoodLevel.NORMAL: "🙂 状态一般",
    MoodLevel.TIRED: "😔 有点累",
    MoodLevel.EXHAUSTED: "😴 很疲惫",
}


# Mood → recommended difficulty range (inclusive bounds) + a "sweet spot"
# used to sort tasks by closeness to the ideal difficulty.
MOOD_DIFFICULTY_RANGE = {
    MoodLevel.EXHAUSTED: (Difficulty.VERY_EASY, Difficulty.VERY_EASY),
    MoodLevel.TIRED: (Difficulty.VERY_EASY, Difficulty.NORMAL),
    MoodLevel.NORMAL: (Difficulty.EASY, Difficulty.HARD),
    MoodLevel.ENERGETIC: (Difficulty.NORMAL, Difficulty.VERY_HARD),
}

# Sweet-spot difficulty: the ideal difficulty for this mood.
# Tasks closer to this value rank higher among in-range tasks.
MOOD_SWEET_SPOT = {
    MoodLevel.EXHAUSTED: Difficulty.VERY_EASY,
    MoodLevel.TIRED: Difficulty.EASY,
    MoodLevel.NORMAL: Difficulty.NORMAL,
    MoodLevel.ENERGETIC: Difficulty.HARD,
}


class MoodLog:
    """One mood entry — typically a focus-session lifecycle record."""

    def __init__(
        self,
        mood_before: MoodLevel,
        mood_after: MoodLevel | None = None,
        task_id: str | None = None,
        completed: bool = False,
        log_id: str | None = None,
        timestamp: str | None = None,
    ):
        self.id = log_id or uuid.uuid4().hex[:8]
        self.timestamp = timestamp or datetime.now().isoformat()
        self.mood_before = mood_before
        self.mood_after = mood_after
        self.task_id = task_id
        self.completed = completed

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "mood_before": int(self.mood_before),
            "mood_after": int(self.mood_after) if self.mood_after is not None else None,
            "task_id": self.task_id,
            "completed": self.completed,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MoodLog":
        mb = data.get("mood_before")
        ma = data.get("mood_after")
        return cls(
            mood_before=MoodLevel(mb) if mb is not None else MoodLevel.NORMAL,
            mood_after=MoodLevel(ma) if ma is not None else None,
            task_id=data.get("task_id"),
            completed=data.get("completed", False),
            log_id=data.get("id"),
            timestamp=data.get("timestamp"),
        )


class MoodManager:
    """Tracks current mood, session logs, and recommends tasks for a mood."""

    def __init__(self):
        self.current_mood: MoodLevel | None = None
        self.current_mood_date: str | None = None  # ISO date for "today" check
        self.log_history: list[MoodLog] = []

    # ── Mood state ─────────────────────────────────────────────────
    def set_current_mood(self, mood: MoodLevel):
        self.current_mood = mood
        self.current_mood_date = date.today().isoformat()

    def has_mood_today(self) -> bool:
        return (
            self.current_mood is not None
            and self.current_mood_date == date.today().isoformat()
        )

    # ── Session lifecycle ──────────────────────────────────────────
    def start_session(self, task_id: str | None, mood_before: MoodLevel) -> MoodLog:
        log = MoodLog(mood_before=mood_before, task_id=task_id)
        self.log_history.append(log)
        return log

    def complete_session(
        self,
        log_entry: MoodLog,
        mood_after: MoodLevel,
        completed: bool = True,
    ):
        log_entry.mood_after = mood_after
        log_entry.completed = completed

    # ── Recommendation algorithm ───────────────────────────────────
    def recommend_tasks(self, tasks: list[Task], mood: MoodLevel) -> list[Task]:
        """Return undone tasks sorted by best fit for the given mood.

        - Drops done tasks.
        - Tasks within the mood's range come first, ordered by closeness
          to the sweet-spot difficulty (tie-broken by original order).
        - Tasks outside the range come after, also ordered by closeness.
        """
        if not tasks:
            return []

        sweet_spot = MOOD_SWEET_SPOT[mood]
        lo, hi = MOOD_DIFFICULTY_RANGE[mood]

        pending = [t for t in tasks if not t.done]

        def sort_key(t: Task):
            in_range = lo <= t.difficulty <= hi
            distance = abs(int(t.difficulty) - int(sweet_spot))
            # in-range first (False sorts before True when negated => 0 before 1)
            return (0 if in_range else 1, distance, t.order)

        return sorted(pending, key=sort_key)

    # ── Serialization ──────────────────────────────────────────────
    def to_dict(self) -> dict:
        return {
            "current_mood": int(self.current_mood) if self.current_mood is not None else None,
            "current_mood_date": self.current_mood_date,
            "log_history": [log.to_dict() for log in self.log_history],
        }

    def load_from_dict(self, data: dict):
        cm = data.get("current_mood")
        self.current_mood = MoodLevel(cm) if cm is not None else None
        self.current_mood_date = data.get("current_mood_date")
        self.log_history = [MoodLog.from_dict(d) for d in data.get("log_history", [])]
