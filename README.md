# LazyTom

A Pomodoro timer app with a points system, designed by a kid with procrastination tendencies.

Built with [Flet](https://flet.dev) (Python).

## Quick Start

```bash
pip install -r requirements.txt
flet run main.py
```

## Run Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

## Project Structure

- `main.py` — App entry point with navigation
- `theme.py` — Colors, fonts, spacing constants
- `timer_engine.py` — Pomodoro timer logic (pure Python)
- `points_engine.py` — Points system logic (pure Python)
- `storage.py` — JSON file persistence
- `views/` — Page-level screens (timer, points, settings)
- `components/` — Reusable UI widgets (countdown ring, controls, badge)
- `tests/` — Unit tests for engines
