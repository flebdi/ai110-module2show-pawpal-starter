# PawPal+ (Module 2 Project)

**PawPal+** is a Streamlit app that helps a pet owner plan care tasks for their pet(s) based on constraints like time, priority, and preferences.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

## Architecture

The system is built around four classes in `pawpal_system.py`:

| Class | Role |
|---|---|
| `Task` | Data for a single care activity (time, priority, frequency, completion) |
| `Pet` | Profile + task list for one animal |
| `Owner` | Container for multiple pets; aggregates all tasks |
| `Scheduler` | Logic layer — sorts, filters, detects conflicts, handles recurrence |

See [uml_final.md](uml_final.md) for the Mermaid.js class diagram.

## Features

- **Add owner and pets** — register named animals under an owner profile via the sidebar.
- **Schedule tasks** — attach timed, prioritized care activities with a due date and frequency.
- **Today's schedule** — view tasks filtered to today, sorted chronologically.
- **Smarter scheduling:**
  - **Sorting by time** — tasks are always presented in `HH:MM` chronological order.
  - **Sorting by priority** — alternate sort from high to low priority.
  - **Filtering** — filter tasks by pet, by completion status, or both.
  - **Conflict warnings** — the scheduler detects two tasks scheduled at the exact same time and surfaces a warning in the UI.
  - **Daily / weekly recurrence** — marking a recurring task complete automatically creates the next occurrence (tomorrow for daily, next week for weekly).
- **Mark complete** — pick any pending task from a dropdown; the app marks it done and schedules the next occurrence if needed.

## Getting Started

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the CLI demo

```bash
python main.py
```

### Launch the Streamlit UI

```bash
streamlit run app.py
```

## Testing PawPal+

```bash
python -m pytest
```

The test suite (`tests/test_pawpal.py`) covers 16 behaviors:

- Task completion status changes
- Pet task count after add/remove
- Owner aggregation across multiple pets
- Case-insensitive pet lookup
- Chronological sort correctness
- Today's schedule excludes future-dated tasks
- Filtering by status and pet name
- Conflict detection (same-time tasks flagged; different-time tasks not flagged)
- Daily recurrence creates a task for the next day
- Weekly recurrence creates a task 7 days later
- One-time tasks produce no recurrence

**Confidence level: 4 / 5 stars** — all 16 tests pass; duration-overlap detection and empty-pet edge cases remain for a future iteration.

## 📸 Demo

> Add a screenshot of the running Streamlit app here.
>
> `<a href="your_screenshot.png" target="_blank"><img src="your_screenshot.png" title="PawPal App" width="" alt="PawPal App" class="center-block" /></a>`

## Suggested Workflow (for instructors / reviewers)

1. Read the scenario above and identify requirements.
2. Review [uml_final.md](uml_final.md) for the class diagram.
3. Inspect `pawpal_system.py` for the logic layer.
4. Run `python main.py` for a CLI demo of sorting, filtering, recurrence, and conflict detection.
5. Run `python -m pytest` to verify all tests pass.
6. Run `streamlit run app.py` to use the full UI.
7. Read [reflection.md](reflection.md) for design decisions and AI collaboration notes.
