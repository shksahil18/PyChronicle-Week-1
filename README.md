# PyChronicle - AST Powered Time Travel Debugger

PyChronicle is a Python developer tool that analyzes Python source files using AST and stores variable assignment history into SQLite.

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

### Terminal User Interface (Textual)

- Initialized a Textual application
- Created a source code view pane
- Added a timeline panel placeholder
- Designed the initial UI layout for future execution timeline navigation

## Run the project

```bash
python -m pychronicle.main

## Current Status

- ✅ Week 1 Completed
- ✅ Week 2 Completed
- 🔄 Week 3: Runtime timeline visualization (Upcoming)


## Technologies Used

- Python 3
- AST (`ast`)
- Runtime Tracing (`sys.settrace`)
- SQLite
- Textual


## SQLite Schema

```sql
CREATE TABLE variable_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    line_number INTEGER NOT NULL,
    variable_name TEXT NOT NULL,
    serialized_value TEXT
);
