import streamlit as st
from datetime import datetime

from pawpal_system import CarePlan, Owner, Pet, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        owner_id="owner-001",
        name="Jordan",
        email="jordan@example.com",
        phone="555-0101",
    )

owner = st.session_state.owner

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
    st.session_state.owner = owner
    st.success(f"{pet.name} was added to {owner.name}'s profile.")

if owner.pets:
    st.subheader("Your pets")
    for pet in owner.pets:
        st.write(f"- {pet.name} ({pet.species})")
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Add a task")
st.caption("This uses the real Pet and Task model classes from the backend.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

if owner.pets:
    selected_pet = st.selectbox("Pet", [pet.name for pet in owner.pets])
    pet = next(p for p in owner.pets if p.name == selected_pet)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    if st.button("Save task"):
        task = Task(
            task_id=f"task-{len(st.session_state.tasks) + 1}",
            title=task_title,
            description=f"{priority.title()} priority task for {pet.name}",
            task_type=priority,
            due_date_time=datetime.now(),
            frequency="daily",
            pet=pet,
        )
        pet.add_task(task)
        st.session_state.tasks.append(task)
        st.success(f"Task '{task.title}' added for {pet.name}.")

    if st.session_state.tasks:
        st.write("Current tasks:")
        for task in st.session_state.tasks:
            st.write(f"- {task.title} ({task.pet.name if task.pet else 'No pet'})")
else:
    st.info("Add a pet before creating tasks.")

st.divider()

st.subheader("Build Schedule")
if st.button("Generate schedule"):
    if owner.pets:
        st.success("Scheduler hook is ready. Connect your scheduling logic here next.")
    else:
        st.warning("Add a pet before generating a schedule.")
