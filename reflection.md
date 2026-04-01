# PawPal+ Project Reflection

---

## 1. System Design

**a. Initial design**

I identified three core user actions the app needed to support:
1. **Add a pet** — register a named animal under an owner profile.
2. **Schedule a task** — attach a timed, prioritized care activity to a specific pet.
3. **View today's tasks** — see a sorted, filtered daily plan with conflict warnings.

From these I derived four classes:

| Class | Responsibility |
|---|---|
| `Task` | Holds all data about one care activity: description, time, duration, priority, frequency, due date, and completion status. |
| `Pet` | Stores pet profile data and owns a list of Tasks. Provides add/remove/get helpers. |
| `Owner` | Manages multiple Pets and aggregates all tasks across them for the Scheduler. |
| `Scheduler` | Stateless coordinator that sorts, filters, detects conflicts, and handles recurrence. It reads from `Owner` but never stores task data itself. |

I used Python `@dataclass` for `Task` and `Pet` to keep attribute initialization clean and avoid writing boilerplate `__init__` methods.

**b. Design changes**

During implementation I made two notable changes:

1. **`pet_name` on `Task`**: The original UML didn't include this field. Once I added conflict detection I realized tasks needed to report which pet they belong to without traversing the whole owner graph. Adding `pet_name` as a denormalized string fixed this cleanly.

2. **`sort_by_priority` method**: The initial plan only had `sort_by_time`. During the algorithmic phase I added a secondary sort keyed on a `priority_weight` property so the UI could let users choose either chronological or urgency order.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

My scheduler considers three constraints:

- **Time** — tasks are sorted by their `HH:MM` string so the daily view is always chronological.
- **Priority** — `high > medium > low`, used as a secondary sort and as a filter dimension in the UI.
- **Due date** — `get_todays_schedule()` filters to only tasks whose `due_date` equals today, so future tasks don't clutter the view.

I prioritized time and due date first because a pet owner's primary question is "what do I need to do *right now*?" Priority matters for choosing what to tackle when two things compete, but the date boundary is the most critical constraint.

**b. Tradeoffs**

**Tradeoff: Exact-minute conflict detection only.**

The conflict detector flags two tasks as conflicting only when their `time` strings match exactly (e.g., both at `"08:00"`). It does not check whether overlapping durations cause a collision (a 60-minute task at 08:00 vs. a 5-minute task at 08:45 would not be flagged even though they technically overlap).

This is reasonable for a pet care app because:
- Most care tasks are discrete, short events (feeding, medication) rather than continuous time blocks.
- Duration-overlap detection would require converting times to `datetime` objects and comparing intervals, adding significant complexity for a relatively rare edge case in real daily schedules.
- A simple exact-time warning is already enough to catch the most common scheduling mistake (two things booked at the same moment).

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude Code (AI) throughout all phases:

- **Design brainstorming** — I described the app's three core user actions and asked the AI to suggest a set of classes with responsibilities. The initial four-class structure came from this conversation.
- **Mermaid UML generation** — the AI generated the class diagram from a natural-language description of attributes and methods.
- **Class skeleton scaffolding** — the AI generated method stubs from the UML in a single step, which I then filled in with real logic.
- **Algorithmic suggestions** — I asked the AI "how should I use a lambda to sort HH:MM strings?" and it provided the `sorted(tasks, key=lambda t: t.time)` pattern.
- **Test generation** — I described the behaviors I wanted to verify and the AI produced the full test file structure; I reviewed each test for correctness before running them.
- **Debugging** — when the Windows terminal raised `UnicodeEncodeError` on emoji characters, the AI immediately identified the cause (cp1252 codec) and swapped in ASCII-safe alternatives.

The most helpful prompt pattern was: "Here is the current state of my file. Given this context, implement X." Providing the file reference kept suggestions grounded in my actual code rather than generic examples.

**b. Judgment and verification**

During test generation, the AI initially suggested mocking `date.today()` using `unittest.mock.patch` to freeze the current date. I rejected this because:

1. Our `Task` dataclass accepts `due_date` as an explicit parameter with a default of `date.today()`. Tests can simply pass a concrete `date` object rather than mocking the global.
2. Mocking `date.today()` globally can interfere with other parts of the stdlib and adds complexity that the design makes unnecessary.

I verified this by reading the `Task` definition, confirming the `due_date` parameter exists, and writing a fixture `def today(): return date.today()` that passes the date explicitly to tasks in tests — no mocking required, and all 16 tests pass.

---

## 4. Testing and Verification

**a. What you tested**

The 16-test suite covers:

- `Task.mark_complete()` flips status from `False` to `True`.
- Tasks default to incomplete at creation.
- `Pet.add_task()` increases task count by 1.
- `Pet.remove_task()` decreases count and returns `True`; unknown IDs return `False`.
- `Owner.get_all_tasks()` aggregates across multiple pets.
- `Owner.find_pet()` is case-insensitive.
- `sort_by_time()` returns tasks in chronological order.
- `get_todays_schedule()` excludes tasks with future `due_date`.
- `filter_by_status()` returns only tasks matching the requested completion state.
- `filter_by_pet()` returns only tasks for the named pet.
- `detect_conflicts()` flags two tasks at the same time; returns no warnings when times differ.
- `mark_task_complete()` on a `daily` task creates a next-day occurrence.
- `mark_task_complete()` on a `weekly` task creates a next-week occurrence.
- `mark_task_complete()` on a `once` task returns `None`.

These tests matter because sorting, filtering, conflict detection, and recurrence are the four algorithmic features that make the app smarter than a plain to-do list.

**b. Confidence**

**4 / 5 stars.** All 16 tests pass and cover the happy paths and the most important edge cases.

What I would test next with more time:
- Duration-overlap conflicts (two tasks whose intervals intersect but start at different minutes).
- An owner with zero pets (edge case for `get_all_tasks()`).
- A pet whose task list is empty feeding into the schedule.
- The Streamlit UI state — ensuring `st.session_state` correctly persists Owner across reruns.

---

## 5. Reflection

**a. What went well**

I am most satisfied with the clean separation between the data layer (`Owner`, `Pet`, `Task`) and the logic layer (`Scheduler`). The Scheduler never stores task data — it only reads from `Owner`. This made the Streamlit integration straightforward: I just attach `Owner` to `st.session_state` and pass it to a fresh `Scheduler` on every rerun without any complex synchronization.

**b. What you would improve**

If I had another iteration I would add **duration-aware conflict detection**. The current exact-minute check is a reasonable MVP but a pet owner scheduling a 60-minute vet visit at 10:00 and a walk at 10:30 would not see a warning, even though they clearly overlap. Implementing interval overlap detection using `datetime.combine` and timedelta arithmetic would make the conflict system genuinely useful.

**c. Key takeaway**

Working with AI as a "lead architect" taught me that AI is excellent at generating *plausible* code quickly, but it doesn't know what *you* need unless you tell it. The most productive moments were when I gave the AI a specific file context and a precise goal ("given this `Task` dataclass, implement `handle_recurrence` so that daily tasks produce a `due_date` of today + 1"). The least productive were vague prompts like "help me with the scheduler." The lesson: AI amplifies clarity — the clearer your design intent, the better the output.
