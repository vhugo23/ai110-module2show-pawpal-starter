# PawPal+ (Module 2 Project)

**PawPal+** is a Streamlit app that helps a busy pet owner stay consistent with pet care. The owner adds pets, schedules care tasks (walks, feeding, meds, grooming), and sees a time-sorted schedule with warnings when two tasks clash. Daily and weekly tasks regenerate automatically when completed.

## System overview

All logic lives in [pawpal_system.py](pawpal_system.py). The design is in [diagrams/uml.mmd](diagrams/uml.mmd) (Mermaid source, same as `uml_final.mmd`).

| Class | Responsibility |
|-------|----------------|
| `Owner` | Owner details and the list of pets. Adds and removes pets and refuses a pet that already belongs to another owner. |
| `Pet` | Pet details, health notes and its tasks. Adds tasks and lists those due today. |
| `Task` | One care activity with a title, due date and time, frequency and completion status. Completing it returns the next occurrence for daily and weekly tasks. |
| `CarePlan` | Groups a pet's tasks and rejects tasks that belong to another pet. |
| `Scheduler` | Works across all pets: schedules tasks, sorts, filters, detects conflicts, completes recurring tasks and builds the daily schedule. |

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the app, demo and tests

```bash
streamlit run app.py       # the Streamlit UI
python main.py             # CLI demo of sorting, filtering, recurrence and conflicts
python -m pytest -v        # the test suite
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## ✨ Features

- **Sorting by time:** `sort_by_time` orders tasks by date, then time, and returns a new list without changing the queue.
- **Filtering:** `filter_tasks` narrows tasks by pet name (case-insensitive), completion status, or both.
- **Conflict warnings:** `detect_conflicts` groups pending tasks by exact start time in one pass and returns a warning for each slot with two or more tasks, for the same pet or for different pets. It never raises, and it ignores completed tasks. Overlapping durations are not detected.
- **Daily and weekly recurrence:** completing a daily task creates the next one 1 day later, and a weekly task 7 days later. The next due time is based on the previous due time, not on when the task was completed. One-off and other frequencies do not repeat.
- **Duplicate-safe completion:** completing a task twice does not create a second next occurrence.
- **Linked data:** adding a task to a pet also adds it to the pet's care plan. A task cannot be scheduled without a pet and a care plan, and a task cannot be added to another pet's care plan.
- **Daily schedule:** `generate_daily_schedule` lists every task due today for an owner's pets.
- **Streamlit UI:** all of the above are available in `app.py`.

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

Start the app with `streamlit run app.py`.

### Main UI features

- **Add a pet:** enter name, species, breed, age and weight. Each pet gets its own care plan.
- **Add a task:** pick a pet, a title, a date, a time and how often it repeats (once, daily or weekly).
- **Build Schedule:** a table of every task, sorted by date and time, with filters for pet and status (all, pending or completed).
- **Conflict warnings:** shown as soon as a task is saved and again beside the schedule, with one warning per clashing time slot.
- **Mark complete:** completes a task. A daily or weekly task shows when its next occurrence is scheduled.

### Example workflow

1. Add a pet, for example Mochi the dog.
2. Add a task "Morning walk" for today at 07:00, repeating daily.
3. Add a second task, "Feed", at the same time. A warning appears saying two tasks share that slot.
4. Look at the schedule table. Tasks are in time order, and the warning names both tasks.
5. Change the "Show status" filter to Pending to see only what is left to do.
6. Select "Morning walk" and press **Mark complete**. The table shows it as completed, and a message says the next walk is tomorrow at 07:00.

### Scheduler behaviors shown

- **Sorting:** tasks added out of order are displayed chronologically.
- **Filtering:** by pet name and by completion status, alone or together.
- **Conflict warnings:** two pending tasks at the same start time are flagged, for the same pet or for different pets.
- **Recurrence:** daily tasks reappear after 1 day, weekly tasks after 7 days, and one-off tasks do not repeat.

### Sample CLI output

`python main.py` runs these behaviors without the UI:

```
As added (out of order):
  10-20 18:30  Evening walk   Buddy  Pending
  10-20 07:45  Breakfast      Luna   Pending
  10-20 12:00  Vet meds       Buddy  Completed
  10-20 09:05  Play session   Luna   Pending
  10-20 07:00  Morning walk   Buddy  Completed

Sorted by time:
  10-20 07:00  Morning walk   Buddy  Completed
  10-20 07:45  Breakfast      Luna   Pending
  10-20 09:05  Play session   Luna   Pending
  10-20 12:00  Vet meds       Buddy  Completed
  10-20 18:30  Evening walk   Buddy  Pending

Buddy's tasks (sorted):
  10-20 07:00  Morning walk   Buddy  Completed
  10-20 12:00  Vet meds       Buddy  Completed
  10-20 18:30  Evening walk   Buddy  Pending

Pending tasks (sorted):
  10-20 07:45  Breakfast      Luna   Pending
  10-20 09:05  Play session   Luna   Pending
  10-20 18:30  Evening walk   Buddy  Pending

Completed tasks:
  10-20 12:00  Vet meds       Buddy  Completed
  10-20 07:00  Morning walk   Buddy  Completed

Luna + pending:
  10-20 07:45  Breakfast      Luna   Pending
  10-20 09:05  Play session   Luna   Pending

Completing recurring tasks...
  T-001 done -> next: T-001@20261021 due Wed 2026-10-21 18:30
  T-002 done -> next: T-002@20261021 due Wed 2026-10-21 07:45
  T-006 done -> next: T-006@20261027 due Tue 2026-10-27 10:00
  T-007 (one-off) done -> next: None

Pending after recurrence:
  10-20 09:05  Play session   Luna   Pending
  10-21 07:45  Breakfast      Luna   Pending
  10-21 18:30  Evening walk   Buddy  Pending
  10-27 10:00  Grooming       Luna   Pending

Buddy's pet.tasks count: 5 | care plan active: 1

Conflict check (before adding clashes): none

Conflict check (after adding clashes):
  WARNING: 2 tasks at 2026-10-20 14:00 (same pet): 'Nail trim' (Buddy), 'Brush teeth' (Buddy)
  WARNING: 2 tasks at 2026-10-20 16:30 (different pets): 'Litter box' (Luna), 'Training' (Buddy)
```

The dates are the day the script ran; yours will show today's date.
