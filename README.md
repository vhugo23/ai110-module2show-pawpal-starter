# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

## 🧪 Testing PawPal+

Install pytest once (`pip install pytest`), then run the suite from the project root:

```bash
python -m pytest -v
```

The 16 tests in [tests/test_pawpal.py](tests/test_pawpal.py) use a fixed date, so results do not depend on the day they run. They cover:

- **Sorting:** tasks added out of order come back chronologically, date is compared before time, the original queue is not modified, and an empty queue returns `[]`.
- **Recurrence:** completing a daily task creates a pending task due the next day and links it to the same pet, care plan and scheduler. Weekly tasks recur after 7 days, one-off tasks do not recur, completing twice creates only one next task, month boundaries work, and an unknown task id raises `ValueError`.
- **Conflict detection:** identical start times are flagged for the same pet and for different pets. Times one minute apart, completed tasks and an empty queue produce no warnings.
- **Empty pet:** a pet with no tasks returns empty results and does not crash.

Sample test output:

```
============================= test session starts =============================
platform win32 -- Python 3.12.2, pytest-9.1.1, pluggy-1.7.0 -- C:\Users\vhugo\Downloads\ai110-module2show-pawpal-starter\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\vhugo\Downloads\ai110-module2show-pawpal-starter
collecting ... collected 16 items

tests/test_pawpal.py::test_sort_by_time_returns_chronological_order PASSED [  6%]
tests/test_pawpal.py::test_sort_by_time_orders_by_date_before_time PASSED [ 12%]
tests/test_pawpal.py::test_sort_by_time_does_not_mutate_queue PASSED     [ 18%]
tests/test_pawpal.py::test_sort_by_time_with_no_tasks_returns_empty_list PASSED [ 25%]
tests/test_pawpal.py::test_completing_daily_task_creates_next_day_task PASSED [ 31%]
tests/test_pawpal.py::test_completing_weekly_task_creates_task_seven_days_later PASSED [ 37%]
tests/test_pawpal.py::test_one_off_task_does_not_recur PASSED            [ 43%]
tests/test_pawpal.py::test_completing_a_task_twice_does_not_duplicate_recurrence PASSED [ 50%]
tests/test_pawpal.py::test_recurrence_crosses_month_boundary PASSED      [ 56%]
tests/test_pawpal.py::test_mark_complete_unknown_task_raises PASSED      [ 62%]
tests/test_pawpal.py::test_detect_conflicts_flags_same_time_same_pet PASSED [ 68%]
tests/test_pawpal.py::test_detect_conflicts_flags_same_time_different_pets PASSED [ 75%]
tests/test_pawpal.py::test_detect_conflicts_ignores_different_times PASSED [ 81%]
tests/test_pawpal.py::test_detect_conflicts_ignores_completed_tasks PASSED [ 87%]
tests/test_pawpal.py::test_detect_conflicts_with_no_tasks_returns_empty_list PASSED [ 93%]
tests/test_pawpal.py::test_pet_with_no_tasks_has_nothing_due_today PASSED [100%]

============================= 16 passed in 0.05s ==============================
```

**Confidence level: ★★★★☆ (4/5).** All 16 tests pass, and they cover the three core scheduling behaviors (sorting, recurrence, conflict detection) including their main edge cases. One star is held back because some code has no tests: `filter_tasks`, the owner/pet/care plan linking and `remove_pet`, the "due today" methods (including whether completed tasks should appear), and the Streamlit UI in `app.py`. Conflict detection also only catches identical start times, not overlapping durations.

## 📐 Smarter Scheduling

All scheduling logic lives in [pawpal_system.py](pawpal_system.py) and is demonstrated end to end by `python main.py`.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Chronological order (date, then time) |
| Filtering | `Scheduler.filter_tasks()` | By pet name and/or completion status |
| Conflict handling | `Scheduler.detect_conflicts()` | Warns when 2+ pending tasks share a start time |
| Recurring tasks | `Task.create_next_occurrence()`, `Scheduler.mark_task_complete()` | Daily (+1 day) and weekly (+7 days) |

### Sorting

`Scheduler.sort_by_time(tasks=None)` returns tasks in chronological order using
`sorted(tasks, key=lambda task: task.due_date_time)`. It sorts the scheduler's
`task_queue` unless you pass your own list, and it returns a new list rather than
modifying the original.

### Filtering

`Scheduler.filter_tasks(tasks=None, pet_name=None, completed=None)` narrows a task
list by pet name (case-insensitive), completion status, or both. Leaving a
parameter as `None` skips that filter. The result can be passed straight to
`sort_by_time`:

```python
scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Buddy", completed=False))
```

### Conflict detection

`Scheduler.detect_conflicts(tasks=None)` uses a lightweight strategy: it groups
pending tasks by exact start time in a single pass (O(n)) and returns a list of
warning strings, one per time slot with two or more tasks. Each warning names the
tasks and pets involved and says whether the clash is for the same pet or
different pets. It never raises, so the caller decides how to show the warnings.
Completed tasks are ignored.

```
WARNING: 2 tasks at 2026-10-20 14:00 (same pet): 'Nail trim' (Buddy), 'Brush teeth' (Buddy)
```

**Limitation:** only identical start times are flagged. Tasks have no duration
yet, so partially overlapping tasks are not detected.

### Recurring tasks

Tasks with frequency `"daily"` or `"weekly"` (case-insensitive) regenerate when
completed.

- `Task.create_next_occurrence()` builds the next task by adding a `timedelta`
  (1 day or 1 week, defined in `RECURRENCE_INTERVALS`) to the current due time,
  and returns `None` for any other frequency.
- `Task.mark_complete()` marks the task done and returns the next occurrence.
- `Scheduler.mark_task_complete(task_id)` is the method to call from the app. It
  completes the task, attaches the new one to the same pet and care plan, and adds
  it to the scheduler queue. Calling it again on a completed task does nothing.

The next due date is based on the previous due date, not the completion time, so a
late completion does not shift the routine.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
