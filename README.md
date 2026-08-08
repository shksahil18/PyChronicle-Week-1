# PyChronicle - AST Powered Time Travel Debugger

PyChronicle is a Python time-travel debugger built during a Python internship.
It parses a target file, traces its execution, stores the execution history in
SQLite, and displays that history in a Textual terminal interface.

## Week 1 Progress

### Completed Work

- Created basic project structure.
- Implemented AST parser using Python `ast` module.
- Added functionality to detect variable assignments.
- Extracted variable names and line numbers.
- Designed SQLite storage schema.
- Stored detected assignments into SQLite database.

## Week 1 Features

- Reads a target Python source file
- Parses code using Python AST
- Detects standard assignments
- Detects annotated assignments
- Detects chained assignments
- Extracts line numbers and variable names
- Stores assignment information in SQLite
- Handles missing files and syntax errors

## Week 2 Features

### Runtime Execution Tracer

- Implemented execution tracing using Python `sys.settrace()`
- Captured execution flow of the target script
- Recorded runtime variable states
- Integrated runtime tracing with the existing project workflow
- Built a Textual-based terminal UI
- Added dynamic execution timeline loaded from SQLite

### Terminal User Interface (Textual)

- Initialized a Textual application
- Created a source code view pane
- Added a timeline panel placeholder
- Designed the initial UI layout for future execution timeline navigation

## Week 3 Objectives
* Implement delta compression for execution history.
* Store only changed variable values instead of complete program states.
* Connect the SQLite database with the Textual interface.
* Develop a timeline slider for navigating execution history.
* Highlight the executed source code line while scrubbing through time.

## Current Work
* Developing the delta compression system.
* Optimizing SQLite queries for faster retrieval.
* Connecting execution records with the terminal interface.
* Designing the timeline navigation system.
* Improving overall performance and reducing memory usage.

## Next Steps (Week 4)
* Package PyChronicle as a command-line application.
* Add watch variables for tracking selected values.
* Improve the user interface and overall experience.
* Prepare the project for final testing and documentation.


## Current Status

- ✅ Week 1: Completed
- ✅ Week 2: Completed
- ✅ Week 3: Completed
- 🔄 Week 4: UpComing


## Week 3: delta-compressed execution history

Earlier versions wrote the entire `frame.f_locals` snapshot at every executed
line. That repeats the same data as a program grows its local state. Week 3
stores a compact delta for every timeline event instead:

```json
{
  "set": {"total": "30"},
  "deleted": []
}
```

- `set` contains only variables that are new or whose `repr()` value changed.
- `deleted` records variables that left the frame.
- Events with no variable change are still retained so control-flow steps are
  visible in the timeline.
- `timeline.py` rebuilds any historical state by applying deltas in order.

For traces with many stable variables, this removes repeated snapshots and is
designed to reduce storage substantially (often around 90% for long-running
programs with small per-line changes). Values are stored as `repr()` strings,
so arbitrary Python values can be inspected without requiring JSON support.

## New and updated files

```text
PyChronicle/
├── data/
│   └── pychronicle.db             # SQLite trace database
├── pychronicle/
│   ├── __init__.py
│   ├── ast_parser.py              # Week 1
│   ├── delta.py                   # Week 3: create/apply compact changes
│   ├── storage.py                 # Week 3: run-scoped delta persistence
│   ├── tracer.py                  # Week 3: save changed variables only
│   ├── timeline.py                # Week 3: reconstruct historical state
│   ├── ui.py                      # Week 3: keyboard/mouse time scrubbing
│   └── main.py                    # Week 3: CLI integration
├── sample_target.py
└── README.md
```

## Database model

The original `variable_history` and `runtime_history` tables are left intact
for Week 1–2 compatibility. Week 3 adds:

```sql
CREATE TABLE execution_runs (
    run_id TEXT PRIMARY KEY,
    target_file TEXT NOT NULL,
    started_at TEXT NOT NULL
);

CREATE TABLE execution_deltas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    step_index INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    line_number INTEGER NOT NULL,
    source_line TEXT NOT NULL,
    delta_json TEXT NOT NULL,
    UNIQUE (run_id, step_index)
);
```

Each tracing session gets a new `run_id`; the UI selects the latest run for the
chosen target file, so older runs do not mix with the current timeline.

## Run it

Activate the virtual environment if needed and run:

```powershell
.\.venv\Scripts\python.exe -m pychronicle.main
```

Trace a different Python file:

```powershell
.\.venv\Scripts\python.exe -m pychronicle.main path\to\program.py
```

For an automated/non-interactive trace without opening Textual:

```powershell
.\.venv\Scripts\python.exe -m pychronicle.main --no-ui
```

## Time-scrubbing UI

The Textual screen loads the persisted delta events from SQLite and contains:

- a source pane that highlights the exact selected execution line;
- a timeline pane showing nearby historical events and their changed names;
- a reconstructed-state pane showing every variable at that point in time;
- an interactive timeline slider.

Use `Left` / `Right` to move one event, `Home` / `End` to jump to the first or
last event, or click the slider to jump through the run. The source highlighter
and reconstructed variable state update together.

## Development and verification

The main implementation order for Week 3 was:

1. `delta.py` — build and apply `{set, deleted}` deltas.
2. `storage.py` — persist and query run-scoped delta events.
3. `tracer.py` — compare current locals to the previous state.
4. `timeline.py` — reconstruct historical state from database events.
5. `ui.py` — add the interactive slider, navigation, and line highlight.
6. `main.py` — connect tracing, persistence, and UI.

Quick verification commands:

```powershell
.\.venv\Scripts\python.exe -m compileall -q pychronicle
.\.venv\Scripts\python.exe -m pychronicle.main --no-ui
```


