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

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

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
