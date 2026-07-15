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

## Run the project

```bash
python -m pychronicle.main

## SQLite Schema

```sql
CREATE TABLE variable_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    line_number INTEGER NOT NULL,
    variable_name TEXT NOT NULL,
    serialized_value TEXT
);
