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

- Read target Python file.
- Parse source code into Abstract Syntax Tree.
- Identify assignment statements.
- Store assignment data in SQLite.

## SQLite Schema

```sql
CREATE TABLE variable_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    line_number INTEGER NOT NULL,
    variable_name TEXT NOT NULL,
    serialized_value TEXT
);
