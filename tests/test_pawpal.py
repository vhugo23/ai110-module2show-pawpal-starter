from datetime import date, datetime, timedelta

import pytest

from pawpal_system import CarePlan, Owner, Pet, Scheduler, Task

BASE = datetime(2030, 1, 15, 9, 0)  # fixed date so tests never depend on "today"


def make_setup(pet_name="Buddy"):
    """Build an owner, pet, care plan and empty scheduler wired together."""
    owner = Owner("O-1", "Ava", "ava@example.com", "555-0101")
    pet = Pet("P-1", pet_name, "Dog", "Lab", 3, 25.0)
    owner.add_pet(pet)
    plan = CarePlan("CP-1", pet, owner, BASE.date())
    pet.care_plan = plan
    return owner, pet, plan, Scheduler()


def add_task(pet, scheduler, task_id, due, frequency="Once", title=None):
    """Create a task, attach it to the pet (and its plan) and queue it."""
    task = Task(task_id, title or task_id, "desc", "Care", due, frequency)
    pet.add_task(task)
    scheduler.schedule_task(task)
    return task


# ---------- Sorting correctness ----------

def test_sort_by_time_returns_chronological_order():
    _, pet, _, sched = make_setup()
    evening = add_task(pet, sched, "T-eve", BASE.replace(hour=17))
    morning = add_task(pet, sched, "T-morn", BASE.replace(hour=8))
    noon = add_task(pet, sched, "T-noon", BASE.replace(hour=12))

    assert sched.sort_by_time() == [morning, noon, evening]


def test_sort_by_time_orders_by_date_before_time():
    _, pet, _, sched = make_setup()
    tomorrow_early = add_task(pet, sched, "T-1", BASE.replace(hour=6) + timedelta(days=1))
    today_late = add_task(pet, sched, "T-2", BASE.replace(hour=22))

    assert sched.sort_by_time() == [today_late, tomorrow_early]


def test_sort_by_time_does_not_mutate_queue():
    _, pet, _, sched = make_setup()
    late = add_task(pet, sched, "T-late", BASE.replace(hour=20))
    early = add_task(pet, sched, "T-early", BASE.replace(hour=7))

    sched.sort_by_time()

    assert sched.task_queue == [late, early]  # original insertion order kept


def test_sort_by_time_with_no_tasks_returns_empty_list():
    _, _, _, sched = make_setup()
    assert sched.sort_by_time() == []


# ---------- Recurrence logic ----------

def test_completing_daily_task_creates_next_day_task():
    _, pet, plan, sched = make_setup()
    walk = add_task(pet, sched, "T-walk", BASE, frequency="Daily")

    next_task = sched.mark_task_complete("T-walk")

    assert walk.is_completed
    assert next_task is not None
    assert next_task.due_date_time == BASE + timedelta(days=1)
    assert not next_task.is_completed
    # The new task must be wired into the pet, care plan and scheduler.
    assert next_task.pet is pet
    assert next_task in plan.tasks
    assert next_task in pet.tasks
    assert next_task in sched.task_queue


def test_completing_weekly_task_creates_task_seven_days_later():
    _, pet, _, sched = make_setup()
    add_task(pet, sched, "T-bath", BASE, frequency="weekly")

    next_task = sched.mark_task_complete("T-bath")

    assert next_task.due_date_time == BASE + timedelta(weeks=1)


def test_one_off_task_does_not_recur():
    _, pet, _, sched = make_setup()
    add_task(pet, sched, "T-vet", BASE, frequency="Once")

    assert sched.mark_task_complete("T-vet") is None
    assert len(sched.task_queue) == 1


def test_completing_a_task_twice_does_not_duplicate_recurrence():
    _, pet, _, sched = make_setup()
    add_task(pet, sched, "T-walk", BASE, frequency="Daily")

    sched.mark_task_complete("T-walk")
    second = sched.mark_task_complete("T-walk")

    assert second is None
    assert len(sched.task_queue) == 2  # original + exactly one next occurrence


def test_recurrence_crosses_month_boundary():
    _, pet, _, sched = make_setup()
    add_task(pet, sched, "T-walk", datetime(2030, 1, 31, 9, 0), frequency="Daily")

    next_task = sched.mark_task_complete("T-walk")

    assert next_task.due_date_time == datetime(2030, 2, 1, 9, 0)


def test_mark_complete_unknown_task_raises():
    _, _, _, sched = make_setup()
    with pytest.raises(ValueError):
        sched.mark_task_complete("does-not-exist")


# ---------- Conflict detection ----------

def test_detect_conflicts_flags_same_time_same_pet():
    _, pet, _, sched = make_setup()
    add_task(pet, sched, "T-1", BASE, title="Walk")
    add_task(pet, sched, "T-2", BASE, title="Feed")

    warnings = sched.detect_conflicts()

    assert len(warnings) == 1
    assert "Walk" in warnings[0] and "Feed" in warnings[0]
    assert "same pet" in warnings[0]


def test_detect_conflicts_flags_same_time_different_pets():
    owner, buddy, _, sched = make_setup("Buddy")
    whiskers = Pet("P-2", "Whiskers", "Cat", "Tabby", 2, 4.0)
    owner.add_pet(whiskers)
    whiskers.care_plan = CarePlan("CP-2", whiskers, owner, BASE.date())
    add_task(buddy, sched, "T-1", BASE, title="Walk")
    add_task(whiskers, sched, "T-2", BASE, title="Groom")

    warnings = sched.detect_conflicts()

    assert len(warnings) == 1
    assert "different pets" in warnings[0]


def test_detect_conflicts_ignores_different_times():
    _, pet, _, sched = make_setup()
    add_task(pet, sched, "T-1", BASE)
    add_task(pet, sched, "T-2", BASE + timedelta(minutes=1))

    assert sched.detect_conflicts() == []


def test_detect_conflicts_ignores_completed_tasks():
    _, pet, _, sched = make_setup()
    add_task(pet, sched, "T-1", BASE)
    add_task(pet, sched, "T-2", BASE).is_completed = True

    assert sched.detect_conflicts() == []


def test_detect_conflicts_with_no_tasks_returns_empty_list():
    _, _, _, sched = make_setup()
    assert sched.detect_conflicts() == []


# ---------- Empty pet ----------

def test_pet_with_no_tasks_has_nothing_due_today():
    owner, pet, _, sched = make_setup()
    assert pet.get_tasks_due_today() == []
    assert sched.generate_daily_schedule(owner) == []
