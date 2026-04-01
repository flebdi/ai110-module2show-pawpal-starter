# PawPal+ UML Class Diagram

```mermaid
classDiagram
    class Task {
        +str id
        +str description
        +str time
        +int duration_minutes
        +str priority
        +str frequency
        +str pet_name
        +date due_date
        +bool completed
        +mark_complete()
        +priority_weight int
    }

    class Pet {
        +str name
        +str species
        +str breed
        +list~Task~ tasks
        +add_task(task)
        +get_tasks() list~Task~
        +remove_task(task_id) bool
    }

    class Owner {
        +str name
        +list~Pet~ pets
        +add_pet(pet)
        +find_pet(name) Pet
        +get_all_tasks() list~Task~
    }

    class Scheduler {
        +Owner owner
        +get_todays_schedule() list~Task~
        +sort_by_time(tasks) list~Task~
        +sort_by_priority(tasks) list~Task~
        +filter_by_status(tasks, completed) list~Task~
        +filter_by_pet(tasks, pet_name) list~Task~
        +filter_pending() list~Task~
        +detect_conflicts(tasks) list~str~
        +handle_recurrence(task) Task
        +mark_task_complete(task) Task
        +print_schedule(tasks)
    }

    Owner "1" --> "*" Pet : owns
    Pet "1" --> "*" Task : has
    Scheduler --> Owner : manages
```

## Relationships

- **Owner → Pet**: One owner can have many pets (`add_pet`, `find_pet`).
- **Pet → Task**: Each pet holds its own task list (`add_task`, `get_tasks`, `remove_task`).
- **Scheduler → Owner**: The Scheduler holds a reference to the Owner and traverses pets to collect all tasks.

## Design Notes

- `Task` is a Python dataclass for clean initialization with default values.
- `Pet` is a dataclass whose `tasks` field is a mutable list (not shared across instances thanks to `field(default_factory=list)`).
- `Scheduler` is a plain class — it coordinates logic but does not own data; data lives in `Owner` and `Pet`.
- Conflict detection uses exact-minute matching as a deliberate tradeoff (see reflection.md § 2b).
