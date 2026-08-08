# PyChronicle - AST Powered Time Travel Debugger

PyChronicle is a Python time-travel debugger built during a Python internship.
It parses a target file, traces its execution, stores the execution history in
SQLite, and displays that history in a Textual terminal interface.

## Week 1 Progress

### Completed Work

* Created basic project structure.
* Implemented AST parser using Python `ast` module.
* Added functionality to detect variable assignments.
* Extracted variable names and line numbers.
* Designed SQLite storage schema.
* Stored detected assignments into SQLite database.

## Week 1 Features

* Reads a target Python source file
* Parses code using Python AST
* Detects standard assignments
* Detects annotated assignments
* Detects chained assignments
* Extracts line numbers and variable names
* Stores assignment information in SQLite
* Handles missing files and syntax errors

## Week 2 Features

### Runtime Execution Tracer

* Implemented execution tracing using Python `sys.settrace()`
* Captured execution flow of the target script
* Recorded runtime variable states
* Integrated runtime tracing with the existing project workflow
* Built a Textual-based terminal UI
* Added dynamic execution timeline loaded from SQLite

### Terminal User Interface (Textual)

* Initialized a Textual application
* Created a source code view pane
* Added a timeline panel placeholder
* Designed the initial UI layout for future execution timeline navigation

## Week 3 Objectives

* Implement delta compression for execution history.
* Store only changed variable values instead of complete program states.
* Connect the SQLite database with the Textual interface.
* Develop a timeline slider for navigating execution history.
* Highlight the executed source code line while scrubbing through time.

## Week 3 Features

### Delta Compression

* Implemented execution-state delta generation.
* Stores only changed variables between execution steps.
* Tracks newly created and modified variables using `set` values.
* Tracks removed variables using `deleted` values.
* Reduces duplicated state information in the database.
* Supports reconstruction of historical program states.

### SQLite Execution History

* Added run-based execution history storage.
* Added unique `run_id` for every tracing session.
* Stores execution deltas with step indexes.
* Stores executed line numbers and source code.
* Prevents execution history from different runs from being mixed.
* Added database queries for retrieving the latest execution run.
* Added run-scoped delta retrieval for timeline navigation.

### Timeline Navigation

* Reconstructs variable state from persisted execution deltas.
* Supports navigation through individual execution events.
* Displays nearby historical execution events.
* Connects execution steps with their corresponding source lines.

### Time-Scrubbing Interface

* Added an interactive execution timeline.
* Added keyboard navigation using `Left` and `Right`.
* Added `Home` and `End` navigation.
* Added source-line highlighting for the selected execution step.
* Added reconstructed variable state display.
* Connected the UI with persisted SQLite execution history.

## Week 4 Features

### Command-Line Application

* Packaged PyChronicle as a command-line application.
* Added a dedicated CLI entry point for easier execution.
* Added support for tracing a user-provided Python file.
* Added a non-interactive `--no-ui` execution mode.
* Improved command-line usage and execution flow.
* Added package configuration using `pyproject.toml`.

### Watch Variables

* Added support for watching selected variables during execution.
* Allows users to focus on important variables while debugging.
* Displays watched variable values during timeline navigation.
* Keeps watch information synchronized with reconstructed execution states.
* Helps reduce unnecessary information while investigating variable changes.

### User Interface Improvements

* Improved the Textual terminal interface.
* Improved execution timeline navigation.
* Improved source code line highlighting.
* Improved reconstructed-state presentation.
* Improved timeline event information.
* Connected watched variables with the debugging timeline.
* Improved overall readability and debugging workflow.

### Final Testing and Documentation

* Tested AST parsing functionality.
* Tested runtime execution tracing.
* Tested delta generation and state reconstruction.
* Tested SQLite execution history storage.
* Tested timeline navigation and source-line highlighting.
* Tested CLI execution with different target Python files.
* Tested non-interactive tracing using `--no-ui`.
* Verified watch variable functionality.
* Updated project documentation and usage instructions.
* Prepared the project for final demonstration and submission.

## Current Work

* Finalizing CLI packaging and distribution workflow.
* Improving watch variable handling.
* Refining the terminal debugging experience.
* Running final project verification and testing.
* Maintaining project documentation and usage examples.

## Week 4 Final Status

* ✅ CLI application packaged
* ✅ Watch variables implemented
* ✅ Textual UI improved
* ✅ Timeline navigation finalized
* ✅ Source-line highlighting implemented
* ✅ SQLite execution history integrated
* ✅ Delta compression implemented
* ✅ Non-interactive `--no-ui` mode implemented
* ✅ Final testing completed
* ✅ Documentation updated

## Current Status

* ✅ Week 1: Completed
* ✅ Week 2: Completed
* ✅ Week 3: Completed
* ✅ Week 4: Completed

## New and updated files

```text
PyChronicle/
│
├── data/
│   └── pychronicle.db
│
├── pychronicle/
│   ├── __init__.py
│   ├── ast_parser.py
│   ├── delta.py
│   ├── storage.py
│   ├── tracer.py
│   ├── timeline.py
│   ├── ui.py
│   ├── main.py
│   └── cli.py
│
├── pyChronicle_CLI_package/
│   └── pyproject.toml
│
├── sample_target.py
├── README.md
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

### CLI Usage

PyChronicle can also be executed through its command-line interface.

Example:

```powershell
pychronicle path\to\program.py
```

For a non-interactive execution:

```powershell
pychronicle path\to\program.py --no-ui
```

Watch selected variables during debugging:

```powershell
pychronicle path\to\program.py --watch variable_name
```

Multiple variables can be watched when supported by the CLI configuration:

```powershell
pychronicle path\to\program.py --watch x --watch total
```

## Time-scrubbing UI

The Textual screen loads the persisted delta events from SQLite and contains:

* a source pane that highlights the exact selected execution line;
* a timeline pane showing nearby historical events and their changed names;
* a reconstructed-state pane showing every variable at that point in time;
* an interactive timeline slider;
* watch variable information for selected values.

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

### Week 4 Implementation

The main implementation work for Week 4 was:

1. `cli.py` — provide the command-line interface and execution options.
2. `pyproject.toml` — package PyChronicle as a CLI application.
3. `tracer.py` — support watch-variable tracking during execution.
4. `timeline.py` — expose watched values while navigating historical states.
5. `ui.py` — improve timeline navigation, source highlighting, and state display.
6. `main.py` — connect CLI arguments, tracing, storage, timeline, and UI.
7. `README.md` — document installation, execution, CLI usage, and debugging features.

## Project Summary

PyChronicle provides a time-travel debugging workflow for Python programs by
combining AST parsing, runtime tracing, delta-compressed execution history,
SQLite persistence, and a Textual terminal interface.

Instead of only moving forward through a debugging session, PyChronicle records
execution history so developers can navigate backward and forward through
previous execution states, inspect variable changes, and identify the exact
source line where a value changed.

The final system combines:

* Python AST analysis
* Runtime execution tracing with `sys.settrace()`
* Delta-based state compression
* SQLite-based execution history
* Historical state reconstruction
* Interactive timeline navigation
* Source code line highlighting
* Watch variables
* Command-line execution
* Textual terminal UI

This project was developed incrementally across four weeks, with each week
adding a major part of the final time-travel debugging workflow.
