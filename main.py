from datetime import date, datetime, time

from pawpal_system import CarePlan, Owner, Pet, Scheduler, Task


def at(hour: int, minute: int) -> datetime:
    return datetime.combine(date.today(), time(hour, minute))


def show(label: str, tasks: list) -> None:
    print(f"\n{label}")
    for task in tasks:
        print(
            f"  {task.due_date_time:%m-%d %H:%M}  {task.title:<14} "
            f"{task.pet.name:<6} {task.get_status()}"
        )


owner = Owner("O-001", "Ava Smith", "ava@example.com", "555-0101")
buddy = Pet("P-001", "Buddy", "Dog", "Golden Retriever", 3, 28.5)
luna = Pet("P-002", "Luna", "Cat", "Tabby", 5, 4.2)
owner.add_pet(buddy)
owner.add_pet(luna)

for pet, plan_id in ((buddy, "CP-001"), (luna, "CP-002")):
    pet.care_plan = CarePlan(plan_id, pet, owner, date.today())

scheduler = Scheduler()

# Deliberately added out of time order
specs = [
    ("T-001", "Evening walk", buddy, at(18, 30)),
    ("T-002", "Breakfast", luna, at(7, 45)),
    ("T-003", "Vet meds", buddy, at(12, 0)),
    ("T-004", "Play session", luna, at(9, 5)),
    ("T-005", "Morning walk", buddy, at(7, 0)),
]
for task_id, title, pet, when in specs:
    task = Task(task_id, title, title, "General", when, "Daily", pet=pet)
    pet.care_plan.add_task(task)
    scheduler.schedule_task(task)

# Mark a couple complete so status filtering has something to show
scheduler.task_queue[2].mark_complete()  # Vet meds
scheduler.task_queue[4].mark_complete()  # Morning walk

show("As added (out of order):", scheduler.task_queue)
show("Sorted by time:", scheduler.sort_by_time())
show("Buddy's tasks (sorted):", scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Buddy")))
show("Pending tasks (sorted):", scheduler.sort_by_time(scheduler.filter_tasks(completed=False)))
show("Completed tasks:", scheduler.filter_tasks(completed=True))
show("Luna + pending:", scheduler.filter_tasks(pet_name="Luna", completed=False))

# --- Recurring tasks -------------------------------------------------------
print("\nCompleting recurring tasks...")
for task_id in ("T-001", "T-002"):  # Evening walk (Daily), Breakfast (Daily)
    nxt = scheduler.mark_task_complete(task_id)
    print(f"  {task_id} done -> next: {nxt.task_id} due {nxt.due_date_time:%a %Y-%m-%d %H:%M}")

weekly = Task("T-006", "Grooming", "Brush coat", "Care", at(10, 0), "Weekly", pet=luna)
luna.care_plan.add_task(weekly)
scheduler.schedule_task(weekly)
nxt = scheduler.mark_task_complete("T-006")
print(f"  T-006 done -> next: {nxt.task_id} due {nxt.due_date_time:%a %Y-%m-%d %H:%M}")

once = Task("T-007", "Vet visit", "Annual", "Health", at(15, 0), "Once", pet=buddy)
buddy.care_plan.add_task(once)
scheduler.schedule_task(once)
print(f"  T-007 (one-off) done -> next: {scheduler.mark_task_complete('T-007')}")

show("Pending after recurrence:", scheduler.sort_by_time(scheduler.filter_tasks(completed=False)))
print("\nBuddy's pet.tasks count:", len(buddy.tasks), "| care plan active:", len(buddy.care_plan.get_active_tasks()))

# --- Conflict detection ----------------------------------------------------
print("\nConflict check (before adding clashes):", scheduler.detect_conflicts() or "none")

def add(task_id, title, pet, when):
    task = Task(task_id, title, title, "General", when, "Once", pet=pet)
    pet.care_plan.add_task(task)
    scheduler.schedule_task(task)

add("T-008", "Nail trim", buddy, at(14, 0))
add("T-009", "Brush teeth", buddy, at(14, 0))   # same pet, same time
add("T-010", "Litter box", luna, at(16, 30))
add("T-011", "Training", buddy, at(16, 30))     # different pets, same time

print("\nConflict check (after adding clashes):")
for warning in scheduler.detect_conflicts():
    print(" ", warning)
