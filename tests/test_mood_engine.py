"""Full coverage tests for the mood engine."""

import os
import sys
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mood_engine import (
    MoodLevel,
    MOOD_LABELS,
    MOOD_DIFFICULTY_RANGE,
    MOOD_SWEET_SPOT,
    MoodLog,
    MoodManager,
)
from task_engine import Task, Difficulty


# ── Enum / label coverage ─────────────────────────────────────────────
class TestMoodEnum:
    def test_values(self):
        assert MoodLevel.EXHAUSTED == 1
        assert MoodLevel.TIRED == 2
        assert MoodLevel.NORMAL == 3
        assert MoodLevel.ENERGETIC == 4

    def test_labels_contain_all_moods(self):
        for m in MoodLevel:
            assert m in MOOD_LABELS
            assert isinstance(MOOD_LABELS[m], str)
            assert len(MOOD_LABELS[m]) > 0

    def test_label_contents(self):
        assert "💪" in MOOD_LABELS[MoodLevel.ENERGETIC]
        assert "😴" in MOOD_LABELS[MoodLevel.EXHAUSTED]
        assert "🙂" in MOOD_LABELS[MoodLevel.NORMAL]
        assert "😔" in MOOD_LABELS[MoodLevel.TIRED]

    def test_range_table_complete(self):
        for m in MoodLevel:
            assert m in MOOD_DIFFICULTY_RANGE
            assert m in MOOD_SWEET_SPOT

    def test_range_table_values(self):
        assert MOOD_DIFFICULTY_RANGE[MoodLevel.EXHAUSTED] == (Difficulty.VERY_EASY, Difficulty.VERY_EASY)
        assert MOOD_DIFFICULTY_RANGE[MoodLevel.TIRED] == (Difficulty.VERY_EASY, Difficulty.NORMAL)
        assert MOOD_DIFFICULTY_RANGE[MoodLevel.NORMAL] == (Difficulty.EASY, Difficulty.HARD)
        assert MOOD_DIFFICULTY_RANGE[MoodLevel.ENERGETIC] == (Difficulty.NORMAL, Difficulty.VERY_HARD)


# ── MoodLog ───────────────────────────────────────────────────────────
class TestMoodLog:
    def test_creation_defaults(self):
        log = MoodLog(mood_before=MoodLevel.NORMAL)
        assert log.mood_before == MoodLevel.NORMAL
        assert log.mood_after is None
        assert log.task_id is None
        assert log.completed is False
        assert log.id is not None
        assert log.timestamp is not None

    def test_to_dict(self):
        log = MoodLog(
            mood_before=MoodLevel.ENERGETIC,
            mood_after=MoodLevel.NORMAL,
            task_id="t1",
            completed=True,
            log_id="lg1",
            timestamp="2026-01-01T10:00:00",
        )
        d = log.to_dict()
        assert d["id"] == "lg1"
        assert d["mood_before"] == 4
        assert d["mood_after"] == 3
        assert d["task_id"] == "t1"
        assert d["completed"] is True
        assert d["timestamp"] == "2026-01-01T10:00:00"

    def test_to_dict_no_after(self):
        log = MoodLog(mood_before=MoodLevel.TIRED)
        d = log.to_dict()
        assert d["mood_after"] is None

    def test_from_dict(self):
        data = {
            "id": "x",
            "timestamp": "2026-05-16",
            "mood_before": 2,
            "mood_after": 4,
            "task_id": "tk",
            "completed": True,
        }
        log = MoodLog.from_dict(data)
        assert log.mood_before == MoodLevel.TIRED
        assert log.mood_after == MoodLevel.ENERGETIC
        assert log.task_id == "tk"
        assert log.completed is True

    def test_from_dict_missing_after(self):
        log = MoodLog.from_dict({"mood_before": 3})
        assert log.mood_after is None
        assert log.mood_before == MoodLevel.NORMAL

    def test_round_trip(self):
        l1 = MoodLog(
            mood_before=MoodLevel.ENERGETIC,
            mood_after=MoodLevel.NORMAL,
            task_id="abc",
            completed=True,
        )
        l2 = MoodLog.from_dict(l1.to_dict())
        assert l2.id == l1.id
        assert l2.mood_before == l1.mood_before
        assert l2.mood_after == l1.mood_after
        assert l2.task_id == l1.task_id
        assert l2.completed == l1.completed


# ── MoodManager basic ─────────────────────────────────────────────────
class TestMoodManager:
    def test_initial_state(self):
        m = MoodManager()
        assert m.current_mood is None
        assert m.log_history == []
        assert m.has_mood_today() is False

    def test_set_current_mood(self):
        m = MoodManager()
        m.set_current_mood(MoodLevel.ENERGETIC)
        assert m.current_mood == MoodLevel.ENERGETIC
        assert m.has_mood_today() is True

    def test_has_mood_today_old_date(self):
        m = MoodManager()
        m.set_current_mood(MoodLevel.NORMAL)
        m.current_mood_date = "2000-01-01"
        assert m.has_mood_today() is False


# ── Session lifecycle ─────────────────────────────────────────────────
class TestSessionLifecycle:
    def test_start_session(self):
        m = MoodManager()
        log = m.start_session("t1", MoodLevel.NORMAL)
        assert log.task_id == "t1"
        assert log.mood_before == MoodLevel.NORMAL
        assert log.mood_after is None
        assert log.completed is False
        assert len(m.log_history) == 1
        assert m.log_history[0] is log

    def test_start_session_no_task(self):
        m = MoodManager()
        log = m.start_session(None, MoodLevel.TIRED)
        assert log.task_id is None

    def test_complete_session(self):
        m = MoodManager()
        log = m.start_session("t1", MoodLevel.TIRED)
        m.complete_session(log, MoodLevel.NORMAL, completed=True)
        assert log.mood_after == MoodLevel.NORMAL
        assert log.completed is True

    def test_complete_session_failed(self):
        m = MoodManager()
        log = m.start_session("t1", MoodLevel.ENERGETIC)
        m.complete_session(log, MoodLevel.EXHAUSTED, completed=False)
        assert log.completed is False
        assert log.mood_after == MoodLevel.EXHAUSTED


# ── Recommendation algorithm ──────────────────────────────────────────
def _make_tasks() -> list[Task]:
    return [
        Task("Very Easy", Difficulty.VERY_EASY, task_id="ve", order=0),
        Task("Easy", Difficulty.EASY, task_id="e", order=1),
        Task("Normal", Difficulty.NORMAL, task_id="n", order=2),
        Task("Hard", Difficulty.HARD, task_id="h", order=3),
        Task("Very Hard", Difficulty.VERY_HARD, task_id="vh", order=4),
    ]


class TestRecommendation:
    def test_empty_list(self):
        m = MoodManager()
        assert m.recommend_tasks([], MoodLevel.NORMAL) == []

    def test_all_done(self):
        m = MoodManager()
        tasks = _make_tasks()
        for t in tasks:
            t.done = True
        assert m.recommend_tasks(tasks, MoodLevel.NORMAL) == []

    def test_exhausted_only_very_easy_first(self):
        m = MoodManager()
        tasks = _make_tasks()
        ranked = m.recommend_tasks(tasks, MoodLevel.EXHAUSTED)
        # Very easy is in-range — should be first
        assert ranked[0].difficulty == Difficulty.VERY_EASY
        # All other tasks are out-of-range; sorted by closeness to VERY_EASY
        assert [t.difficulty for t in ranked[1:]] == [
            Difficulty.EASY,
            Difficulty.NORMAL,
            Difficulty.HARD,
            Difficulty.VERY_HARD,
        ]

    def test_tired_range(self):
        m = MoodManager()
        tasks = _make_tasks()
        ranked = m.recommend_tasks(tasks, MoodLevel.TIRED)
        in_range = [t for t in ranked if Difficulty.VERY_EASY <= t.difficulty <= Difficulty.NORMAL]
        out_range = [t for t in ranked if not (Difficulty.VERY_EASY <= t.difficulty <= Difficulty.NORMAL)]
        # In-range tasks must come first
        assert ranked[: len(in_range)] == in_range
        # Sweet spot is EASY → first should be EASY
        assert ranked[0].difficulty == Difficulty.EASY

    def test_normal_range(self):
        m = MoodManager()
        tasks = _make_tasks()
        ranked = m.recommend_tasks(tasks, MoodLevel.NORMAL)
        # Sweet spot NORMAL → NORMAL first
        assert ranked[0].difficulty == Difficulty.NORMAL
        # VERY_EASY and VERY_HARD are out-of-range and should be at the end
        assert ranked[-1].difficulty in (Difficulty.VERY_EASY, Difficulty.VERY_HARD)
        assert ranked[-2].difficulty in (Difficulty.VERY_EASY, Difficulty.VERY_HARD)

    def test_energetic_prefers_harder(self):
        m = MoodManager()
        tasks = _make_tasks()
        ranked = m.recommend_tasks(tasks, MoodLevel.ENERGETIC)
        # Sweet spot is HARD → HARD first
        assert ranked[0].difficulty == Difficulty.HARD
        # In-range: NORMAL, HARD, VERY_HARD. VERY_EASY/EASY are out-of-range.
        in_range_diffs = {Difficulty.NORMAL, Difficulty.HARD, Difficulty.VERY_HARD}
        assert ranked[0].difficulty in in_range_diffs
        assert ranked[1].difficulty in in_range_diffs
        assert ranked[2].difficulty in in_range_diffs
        assert ranked[3].difficulty not in in_range_diffs
        assert ranked[4].difficulty not in in_range_diffs

    def test_skips_done_tasks(self):
        m = MoodManager()
        tasks = _make_tasks()
        tasks[2].done = True  # Normal done
        ranked = m.recommend_tasks(tasks, MoodLevel.NORMAL)
        assert all(not t.done for t in ranked)
        assert len(ranked) == 4

    def test_tie_breaks_on_order(self):
        m = MoodManager()
        tasks = [
            Task("A", Difficulty.NORMAL, task_id="a", order=0),
            Task("B", Difficulty.NORMAL, task_id="b", order=1),
            Task("C", Difficulty.NORMAL, task_id="c", order=2),
        ]
        ranked = m.recommend_tasks(tasks, MoodLevel.NORMAL)
        assert [t.name for t in ranked] == ["A", "B", "C"]

    def test_no_in_range_falls_back_to_closest(self):
        m = MoodManager()
        tasks = [
            Task("X", Difficulty.HARD, task_id="x", order=0),
            Task("Y", Difficulty.VERY_HARD, task_id="y", order=1),
        ]
        ranked = m.recommend_tasks(tasks, MoodLevel.EXHAUSTED)
        # Neither is in EXHAUSTED's range; closer to VERY_EASY wins → HARD
        assert ranked[0].difficulty == Difficulty.HARD
        assert ranked[1].difficulty == Difficulty.VERY_HARD


# ── Serialization ─────────────────────────────────────────────────────
class TestSerialization:
    def test_to_dict_empty(self):
        m = MoodManager()
        d = m.to_dict()
        assert d["current_mood"] is None
        assert d["log_history"] == []

    def test_load_from_dict_empty(self):
        m = MoodManager()
        m.load_from_dict({})
        assert m.current_mood is None
        assert m.log_history == []

    def test_round_trip(self):
        m1 = MoodManager()
        m1.set_current_mood(MoodLevel.ENERGETIC)
        log = m1.start_session("t1", MoodLevel.NORMAL)
        m1.complete_session(log, MoodLevel.TIRED, completed=True)
        m1.start_session("t2", MoodLevel.TIRED)

        m2 = MoodManager()
        m2.load_from_dict(m1.to_dict())
        assert m2.current_mood == MoodLevel.ENERGETIC
        assert m2.current_mood_date == date.today().isoformat()
        assert len(m2.log_history) == 2
        assert m2.log_history[0].mood_before == MoodLevel.NORMAL
        assert m2.log_history[0].mood_after == MoodLevel.TIRED
        assert m2.log_history[0].completed is True
        assert m2.log_history[1].task_id == "t2"
        assert m2.log_history[1].mood_after is None

    def test_load_preserves_log_ids(self):
        m1 = MoodManager()
        log = m1.start_session("tx", MoodLevel.NORMAL)
        original_id = log.id
        m2 = MoodManager()
        m2.load_from_dict(m1.to_dict())
        assert m2.log_history[0].id == original_id
