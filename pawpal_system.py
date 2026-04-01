"""
PawPal+ Logic Layer
Handles Owner, Pet, Task, and Scheduler classes for the pet care management system.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """Represents a single pet care activity."""

    description: str
    time: str                        # "HH:MM" (24-hour)
    duration_minutes: int
    priority: str                    # "low" | "medium" | "high"
    frequency: str                   # "once" | "daily" | "weekly"
    pet_name: str
    due_date: date = field(default_factory=date.today)
    completed: bool = False
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    # Priority weights used for secondary sorting
    _PRIORITY_WEIGHT = {"low": 0, "medium": 1, "high": 2}

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    @property
    def priority_weight(self) -> int:
        """Numeric priority so high > medium > low."""
        return self._PRIORITY_WEIGHT.get(self.priority, 0)

    def __str__(self) -> str:
        status = "DONE" if self.completed else "TODO"
        return (
            f"{status} {self.time} | {self.description} "
            f"({self.duration_minutes}min, {self.priority}) "
            f"[{self.frequency}] - {self.pet_name}"
        )


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    """Stores pet details and a list of associated tasks."""

    name: str
    species: str
    breed: str = "Unknown"
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        task.pet_name = self.name
        self.tasks.append(task)

    def get_tasks(self) -> list[Task]:
        """Return all tasks for this pet."""
        return list(self.tasks)

    def remove_task(self, task_id: str) -> bool:
        """Remove a task by ID. Returns True if found and removed."""
        for i, t in enumerate(self.tasks):
            if t.id == task_id:
                self.tasks.pop(i)
                return True
        return False

    def __str__(self) -> str:
        return f"{self.name} ({self.species}, {self.breed})"


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

class Owner:
    """Manages multiple pets and provides unified access to all their tasks."""

    def __init__(self, name: str) -> None:
        """Initialize an Owner with a name and an empty pet list."""
        self.name = name
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def find_pet(self, name: str) -> Optional[Pet]:
        """Look up a pet by name (case-insensitive). Returns None if not found."""
        name_lower = name.lower()
        for pet in self.pets:
            if pet.name.lower() == name_lower:
                return pet
        return None

    def get_all_tasks(self) -> list[Task]:
        """Collect and return every task across all pets."""
        all_tasks: list[Task] = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks

    def __str__(self) -> str:
        return f"Owner: {self.name} ({len(self.pets)} pet(s))"


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    """Brain of PawPal+: retrieves, organizes, and manages tasks across pets."""

    def __init__(self, owner: Owner) -> None:
        """Bind the scheduler to an owner so it can access all pet tasks."""
        self.owner = owner

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def get_todays_schedule(self) -> list[Task]:
        """Return all tasks whose due_date is today, sorted by time."""
        today = date.today()
        todays = [t for t in self.owner.get_all_tasks() if t.due_date == today]
        return self.sort_by_time(todays)

    # ------------------------------------------------------------------
    # Sorting
    # ------------------------------------------------------------------

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks chronologically by their 'HH:MM' time string."""
        return sorted(tasks, key=lambda t: t.time)

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks from highest to lowest priority, then by time."""
        return sorted(tasks, key=lambda t: (-t.priority_weight, t.time))

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def filter_by_status(self, tasks: list[Task], completed: bool) -> list[Task]:
        """Return only tasks matching the given completion status."""
        return [t for t in tasks if t.completed == completed]

    def filter_by_pet(self, tasks: list[Task], pet_name: str) -> list[Task]:
        """Return only tasks belonging to the named pet (case-insensitive)."""
        name_lower = pet_name.lower()
        return [t for t in tasks if t.pet_name.lower() == name_lower]

    def filter_pending(self) -> list[Task]:
        """Shortcut: all incomplete tasks across all pets, sorted by time."""
        return self.sort_by_time(
            self.filter_by_status(self.owner.get_all_tasks(), completed=False)
        )

    # ------------------------------------------------------------------
    # Conflict detection
    # ------------------------------------------------------------------

    def detect_conflicts(self, tasks: Optional[list[Task]] = None) -> list[str]:
        """
        Return a list of warning strings for tasks scheduled at the same time.
        Two tasks conflict when they share the same time string and the same
        due_date. Only exact-minute matches are flagged (a known tradeoff).
        """
        if tasks is None:
            tasks = self.owner.get_all_tasks()

        warnings: list[str] = []
        seen: dict[tuple, list[Task]] = {}

        for task in tasks:
            key = (task.due_date, task.time)
            seen.setdefault(key, []).append(task)

        for (day, time_str), group in seen.items():
            if len(group) > 1:
                names = ", ".join(f'"{t.description}" ({t.pet_name})' for t in group)
                warnings.append(
                    f"WARNING: Conflict at {time_str} on {day}: {names}"
                )

        return warnings

    # ------------------------------------------------------------------
    # Recurring tasks
    # ------------------------------------------------------------------

    def handle_recurrence(self, task: Task) -> Optional[Task]:
        """
        When a task is marked complete, create the next occurrence if recurring.
        Returns the new Task (added to the pet's list) or None for one-time tasks.
        """
        if not task.completed:
            return None
        if task.frequency == "once":
            return None

        delta = timedelta(days=1) if task.frequency == "daily" else timedelta(weeks=1)
        next_due = task.due_date + delta

        next_task = Task(
            description=task.description,
            time=task.time,
            duration_minutes=task.duration_minutes,
            priority=task.priority,
            frequency=task.frequency,
            pet_name=task.pet_name,
            due_date=next_due,
        )

        pet = self.owner.find_pet(task.pet_name)
        if pet:
            pet.add_task(next_task)

        return next_task

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """
        Mark a task complete and, if it recurs, schedule its next occurrence.
        Returns the new Task if one was created, otherwise None.
        """
        task.mark_complete()
        return self.handle_recurrence(task)

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def print_schedule(self, tasks: Optional[list[Task]] = None) -> None:
        """Print a formatted daily schedule to the terminal."""
        if tasks is None:
            tasks = self.get_todays_schedule()

        print(f"\n{'='*55}")
        print(f"  PawPal+ Daily Schedule - {date.today()}")
        print(f"  Owner: {self.owner.name}")
        print(f"{'='*55}")

        if not tasks:
            print("  No tasks scheduled for today.")
        else:
            for task in tasks:
                print(f"  {task}")

        conflicts = self.detect_conflicts(tasks)
        if conflicts:
            print()
            for w in conflicts:
                print(f"  {w}")

        print(f"{'='*55}\n")
