from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional


@dataclass
class Owner:
    owner_id: str
    name: str
    email: str
    phone: str
    pets: List["Pet"] = field(default_factory=list)

    def add_pet(self, pet: "Pet") -> None:
        if pet not in self.pets:
            self.pets.append(pet)
            pet.owner = self

    def remove_pet(self, pet_id: str) -> None:
        self.pets = [pet for pet in self.pets if pet.pet_id != pet_id]

    def update_profile(self, name: str, email: str, phone: str) -> None:
        self.name = name
        self.email = email
        self.phone = phone

    def view_care_plan(self, pet_id: str) -> Optional["CarePlan"]:
        for pet in self.pets:
            if pet.pet_id == pet_id:
                return pet.care_plan
        return None


@dataclass
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
        if task not in self.tasks:
            self.tasks.append(task)
            task.pet = self

    def update_health_status(self, notes: str) -> None:
        self.health_notes = notes

    def get_tasks_due_today(self) -> List["Task"]:
        today = date.today()
        return [task for task in self.tasks if task.due_date_time.date() == today]


@dataclass
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

    def mark_complete(self) -> None:
        self.is_completed = True

    def reschedule(self, new_date_time: datetime) -> None:
        self.due_date_time = new_date_time

    def get_status(self) -> str:
        return "Completed" if self.is_completed else "Pending"


@dataclass
class Scheduler:
    schedule_id: str = "scheduler_default"
    task_queue: List[Task] = field(default_factory=list)

    def schedule_task(self, task: Task) -> None:
        if task not in self.task_queue:
            self.task_queue.append(task)

    def generate_daily_schedule(self, owner: Owner) -> List[Task]:
        daily_tasks: List[Task] = []
        for pet in owner.pets:
            for task in pet.tasks:
                if task.due_date_time.date() == date.today():
                    daily_tasks.append(task)
        return daily_tasks

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
