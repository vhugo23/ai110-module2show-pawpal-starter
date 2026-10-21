from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import DefaultDict, List, Optional

# Frequencies that regenerate when completed, mapped to the gap before the next one.
RECURRENCE_INTERVALS = {
    "daily": timedelta(days=1),
    "weekly": timedelta(weeks=1),
}


@dataclass
class Owner:
    owner_id: str
    name: str
    email: str
    phone: str
    pets: List["Pet"] = field(default_factory=list)

    def add_pet(self, pet: "Pet") -> None:
        if pet in self.pets:
            return
        if pet.owner is not None and pet.owner is not self:
            raise ValueError(f"Pet '{pet.name}' is already assigned to another owner.")
        self.pets.append(pet)
        pet.owner = self

    def remove_pet(self, pet_id: str) -> None:
        pet_to_remove = next((pet for pet in self.pets if pet.pet_id == pet_id), None)
        if pet_to_remove is None:
            return
        self.pets.remove(pet_to_remove)
        pet_to_remove.owner = None
        if pet_to_remove.care_plan is not None:
            pet_to_remove.care_plan.tasks = []
            pet_to_remove.care_plan = None
        pet_to_remove.tasks.clear()

    def update_profile(self, name: str, email: str, phone: str) -> None:
        self.name = name
        self.email = email
        self.phone = phone

    def view_care_plan(self, pet_id: str) -> Optional["CarePlan"]:
        for pet in self.pets:
            if pet.pet_id == pet_id:
                return pet.care_plan
        return None


@dataclass(eq=False)
class Pet:
    pet_id: str
    name: str
    species: str
    breed: str
    age: int
    weight: float
    health_notes: str = ""
    owner: Optional[Owner] = None
    care_plan: Optional["CarePlan"] = None
    tasks: List["Task"] = field(default_factory=list)

    def add_task(self, task: "Task") -> None:
        if task in self.tasks:
            return
        self.tasks.append(task)
        task.pet = self
        if self.care_plan is not None and task not in self.care_plan.tasks:
            self.care_plan.tasks.append(task)
            task.care_plan = self.care_plan

    def update_health_status(self, notes: str) -> None:
        self.health_notes = notes

    def get_tasks_due_today(self) -> List["Task"]:
        today = date.today()
        return [task for task in self.tasks if task.due_date_time.date() == today]


@dataclass(eq=False)
class Task:
    task_id: str
    title: str
    description: str
    task_type: str
    due_date_time: datetime
    frequency: str
    pet: Optional[Pet] = None
    care_plan: Optional["CarePlan"] = None
    is_completed: bool = False

    def mark_complete(self) -> Optional["Task"]:
        """Complete this task; for daily/weekly tasks return the next occurrence."""
        self.is_completed = True
        return self.create_next_occurrence()

    def create_next_occurrence(self) -> Optional["Task"]:
        interval = RECURRENCE_INTERVALS.get(self.frequency.strip().lower())
        if interval is None:
            return None
        base_id = self.task_id.split("@")[0]
        next_due = self.due_date_time + interval
        return Task(
            task_id=f"{base_id}@{next_due:%Y%m%d}",
            title=self.title,
            description=self.description,
            task_type=self.task_type,
            due_date_time=next_due,
            frequency=self.frequency,
        )

    def reschedule(self, new_date_time: datetime) -> None:
        self.due_date_time = new_date_time

    def get_status(self) -> str:
        return "Completed" if self.is_completed else "Pending"


@dataclass
class Scheduler:
    schedule_id: str = "scheduler_default"
    task_queue: List[Task] = field(default_factory=list)

    def schedule_task(self, task: Task) -> None:
        if task in self.task_queue:
            return
        if task.pet is None or task.care_plan is None:
            raise ValueError("A task must belong to a pet and a care plan before scheduling.")
        self.task_queue.append(task)

    def remove_task(self, task_id: str) -> None:
        self.task_queue = [task for task in self.task_queue if task.task_id != task_id]

    def mark_task_complete(self, task_id: str) -> Optional[Task]:
        """Complete a task and, if it recurs, register the next occurrence.

        Returns the newly created task, or None for one-off tasks.
        """
        task = next((t for t in self.task_queue if t.task_id == task_id), None)
        if task is None:
            raise ValueError(f"No scheduled task with id '{task_id}'.")
        if task.is_completed:
            return None
        next_task = task.mark_complete()
        if next_task is None:
            return None
        # Attach to the same pet / care plan so every view stays in sync.
        if task.care_plan is not None:
            next_task.pet = task.pet
            task.care_plan.add_task(next_task)
        elif task.pet is not None:
            task.pet.add_task(next_task)
        self.schedule_task(next_task)
        return next_task

    def generate_daily_schedule(self, owner: Owner) -> List[Task]:
        daily_tasks: List[Task] = []
        for pet in owner.pets:
            for task in pet.tasks:
                if task.due_date_time.date() == date.today():
                    daily_tasks.append(task)
        return daily_tasks

    def sort_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Return tasks in chronological order (date first, then time)."""
        tasks = self.task_queue if tasks is None else tasks
        return sorted(tasks, key=lambda task: task.due_date_time)

    def filter_tasks(
        self,
        tasks: Optional[List[Task]] = None,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> List[Task]:
        """Filter tasks by pet name and/or completion status (None = no filter)."""
        tasks = self.task_queue if tasks is None else tasks
        return [
            task
            for task in tasks
            if (pet_name is None or (task.pet is not None and task.pet.name.lower() == pet_name.lower()))
            and (completed is None or task.is_completed == completed)
        ]

    def detect_conflicts(self, tasks: Optional[List[Task]] = None) -> List[str]:
        """Return a warning string for every time slot holding 2+ pending tasks.

        Lightweight strategy: bucket tasks by exact start time in one pass (O(n))
        instead of comparing every pair. Never raises; an empty list means no
        conflicts. Works across pets as well as within one pet.
        """
        tasks = self.task_queue if tasks is None else tasks
        slots: DefaultDict[datetime, List[Task]] = defaultdict(list)
        for task in tasks:
            if not task.is_completed:
                slots[task.due_date_time].append(task)

        warnings: List[str] = []
        for when, group in sorted(slots.items()):
            if len(group) < 2:
                continue
            names = [f"'{t.title}' ({t.pet.name if t.pet else 'no pet'})" for t in group]
            same_pet = len({t.pet for t in group}) == 1
            scope = "same pet" if same_pet else "different pets"
            warnings.append(f"WARNING: {len(group)} tasks at {when:%Y-%m-%d %H:%M} ({scope}): " + ", ".join(names))
        return warnings

    def check_due_tasks(self) -> List[Task]:
        due_tasks: List[Task] = []
        for task in self.task_queue:
            if task.due_date_time <= datetime.now() and not task.is_completed:
                due_tasks.append(task)
        return due_tasks

    def send_reminder(self, task: Task) -> None:
        pet_name = task.pet.name if task.pet else "your pet"
        print(f"Reminder: {task.title} is due for {pet_name} at {task.due_date_time}")


@dataclass
class CarePlan:
    care_plan_id: str
    pet: Pet
    owner: Owner
    start_date: date
    end_date: Optional[date] = None
    notes: str = ""
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        if task.pet is not self.pet:
            raise ValueError(f"Task '{task.title}' does not belong to pet '{self.pet.name}'.")
        if task not in self.tasks:
            self.tasks.append(task)
            task.care_plan = self
            if task not in self.pet.tasks:
                self.pet.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        self.tasks = [task for task in self.tasks if task.task_id != task_id]
        self.pet.tasks = [task for task in self.pet.tasks if task.task_id != task_id]

    def get_active_tasks(self) -> List[Task]:
        return [task for task in self.tasks if not task.is_completed]

    def update_plan(self, notes: str) -> None:
        self.notes = notes


# Example usage for quick testing
if __name__ == "__main__":
    owner = Owner("O-001", "Ava Smith", "ava@example.com", "555-0101")
    pet = Pet("P-001", "Buddy", "Dog", "Golden Retriever", 3, 28.5, "Healthy and active")
    owner.add_pet(pet)

    care_plan = CarePlan("CP-001", pet, owner, date.today())
    pet.care_plan = care_plan

    task1 = Task(
        "T-001",
        "Walk",
        "Take Buddy for a 30-minute walk",
        "Exercise",
        datetime.now(),
        "Daily",
        pet=pet,
        care_plan=care_plan,
    )
    task2 = Task(
        "T-002",
        "Feed",
        "Feed Buddy breakfast and dinner",
        "Nutrition",
        datetime.now(),
        "Twice daily",
        pet=pet,
        care_plan=care_plan,
    )

    care_plan.add_task(task1)
    care_plan.add_task(task2)

    scheduler = Scheduler()
    scheduler.schedule_task(task1)
    scheduler.schedule_task(task2)

    print(owner.name, pet.name, len(care_plan.tasks), scheduler.generate_daily_schedule(owner))
