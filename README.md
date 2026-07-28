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


# PyChronicle – Week 3 Progress (Ongoing)
## Overview
During Week 3, the primary goal is to transform PyChronicle from a runtime tracer into a true time-travel debugger. The focus is on optimizing data storage, improving performance, and creating an interactive interface that allows developers to move backward and forward through a program's execution history.

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

## Expected Learning Outcomes
* Understand efficient state management.
* Learn delta-based storage techniques.
* Improve database optimization skills.
* Build interactive terminal applications using Textual.
* Gain deeper knowledge of Python metaprogramming.

## Next Steps (Week 4)
* Package PyChronicle as a command-line application.
* Add watch variables for tracking selected values.
* Improve the user interface and overall experience.
* Prepare the project for final testing and documentation.

Week 3 is currently focused on optimizing performance and building the interactive time-travel interface that will allow developers to inspect historical program states efficiently.


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
