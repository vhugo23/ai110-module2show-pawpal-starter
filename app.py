import streamlit as st
from datetime import datetime

from pawpal_system import CarePlan, Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        owner_id="owner-001",
        name="Jordan",
        email="jordan@example.com",
        phone="555-0101",
    )
if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()
if "task_counter" not in st.session_state:
    st.session_state.task_counter = 0

owner = st.session_state.owner
scheduler = st.session_state.scheduler


def conflict_warnings(heading: str) -> None:
    """Show every scheduler conflict as a warning the owner can act on."""
    warnings = scheduler.detect_conflicts()
    if not warnings:
        return
    st.warning(
        f"**{heading}** {len(warnings)} time slot(s) have more than one task. "
        "Reschedule one task in each slot so nothing gets missed."
    )
    for message in warnings:
        st.warning(message.removeprefix("WARNING: "), icon="⚠️")


def complete_task(task_id: str) -> None:
    """Button callback: runs before the rerun, so the table below shows the new state."""
    next_task = scheduler.mark_task_complete(task_id)
    if next_task:
        st.session_state.flash = (
            f"Done! The next '{next_task.title}' is scheduled for "
            f"{next_task.due_date_time:%a %b %d at %H:%M}."
        )
    else:
        st.session_state.flash = "Done! This was a one-time task."


def task_rows(tasks):
    return [
        {
            "Due": task.due_date_time.strftime("%a %b %d, %H:%M"),
            "Pet": task.pet.name if task.pet else "-",
            "Task": task.title,
            "Repeats": task.frequency.title(),
            "Status": "✅ Completed" if task.is_completed else "⏳ Pending",
        }
        for task in tasks
    ]


st.subheader("Owner")
st.write(f"Name: {owner.name}")

with st.form("pet_form"):
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    breed = st.text_input("Breed", value="Mixed breed")
    age = st.number_input("Age", min_value=0, max_value=30, value=2)
    weight = st.number_input("Weight (kg)", min_value=0.1, max_value=200.0, value=8.5, step=0.1)
    submitted = st.form_submit_button("Add pet")

if submitted and pet_name:
    pet = Pet(
        pet_id=f"pet-{len(owner.pets) + 1}",
        name=pet_name,
        species=species,
        breed=breed,
        age=int(age),
        weight=float(weight),
    )
    owner.add_pet(pet)
    # The scheduler requires every task to belong to a care plan.
    pet.care_plan = CarePlan(
        care_plan_id=f"plan-{pet.pet_id}", pet=pet, owner=owner, start_date=datetime.now().date()
    )
    st.success(f"{pet.name} was added to {owner.name}'s profile.")

if owner.pets:
    st.subheader("Your pets")
    for pet in owner.pets:
        st.write(f"- {pet.name} ({pet.species})")
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Add a task")

if owner.pets:
    with st.form("task_form"):
        selected_pet = st.selectbox("Pet", [pet.name for pet in owner.pets])
        col1, col2 = st.columns(2)
        with col1:
            task_title = st.text_input("Task title", value="Morning walk")
            due_date = st.date_input("Date", value=datetime.now().date())
        with col2:
            frequency = st.selectbox("Repeats", ["once", "daily", "weekly"], index=1)
            due_time = st.time_input("Time", value=datetime.now().replace(second=0, microsecond=0).time())
        save_task = st.form_submit_button("Save task")

    if save_task and task_title:
        pet = next(p for p in owner.pets if p.name == selected_pet)
        st.session_state.task_counter += 1
        task = Task(
            task_id=f"task-{st.session_state.task_counter}",
            title=task_title,
            description=f"{task_title} for {pet.name}",
            task_type="care",
            due_date_time=datetime.combine(due_date, due_time),
            frequency=frequency,
            pet=pet,
        )
        pet.add_task(task)
        scheduler.schedule_task(task)
        st.success(f"Task '{task.title}' added for {pet.name}.")
        # Flag a clash right away; the full details appear under "Build Schedule".
        if scheduler.detect_conflicts():
            st.warning("This task overlaps another one. See the conflict details under Build Schedule.")
else:
    st.info("Add a pet before creating tasks.")

st.divider()

st.subheader("Build Schedule")

if "flash" in st.session_state:
    st.success(st.session_state.pop("flash"))

if not scheduler.task_queue:
    st.info("No tasks yet. Add a task above to build a schedule.")
else:
    col1, col2 = st.columns(2)
    with col1:
        pet_filter = st.selectbox("Show pet", ["All pets"] + [p.name for p in owner.pets])
    with col2:
        status_filter = st.selectbox("Show status", ["All", "Pending", "Completed"])

    filtered = scheduler.filter_tasks(
        pet_name=None if pet_filter == "All pets" else pet_filter,
        completed={"All": None, "Pending": False, "Completed": True}[status_filter],
    )
    ordered = scheduler.sort_by_time(filtered)

    if ordered:
        st.caption("Sorted by date and time, earliest first.")
        st.table(task_rows(ordered))
    else:
        st.info("No tasks match these filters.")

    if scheduler.detect_conflicts():
        conflict_warnings("Heads up.")
    else:
        st.success("No scheduling conflicts. Your plan is clear.")

    st.subheader("Mark a task complete")
    pending = scheduler.sort_by_time(scheduler.filter_tasks(completed=False))
    if pending:
        labels = {
            f"{t.due_date_time:%b %d %H:%M} - {t.title} ({t.pet.name if t.pet else '-'})": t.task_id
            for t in pending
        }
        choice = st.selectbox("Task", list(labels))
        st.button("Mark complete", on_click=complete_task, args=(labels[choice],))
    else:
        st.info("All tasks are complete.")
