import sqlite3
import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "pychronicle.db"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


@dataclass(frozen=True)
class ExecutionEvent:
    """A single persisted trace event. Its state is represented as a delta."""

    run_id: str
    step_index: int
    line_number: int
    source_line: str
    delta: dict[str, Any]


def create_table() -> None:
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS variable_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                line_number INTEGER NOT NULL,
                variable_name TEXT NOT NULL,
                serialized_value TEXT
            )
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_variable_line
            ON variable_history(variable_name, line_number)
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS runtime_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                line_number INTEGER NOT NULL,
                source_line TEXT NOT NULL,
                locals_snapshot TEXT NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS execution_runs (
                run_id TEXT PRIMARY KEY,
                target_file TEXT NOT NULL,
                started_at TEXT NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS execution_deltas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                step_index INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                line_number INTEGER NOT NULL,
                source_line TEXT NOT NULL,
                delta_json TEXT NOT NULL,
                FOREIGN KEY (run_id) REFERENCES execution_runs(run_id),
                UNIQUE (run_id, step_index)
            )
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_execution_deltas_run_step
            ON execution_deltas(run_id, step_index)
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_execution_runs_target_started
            ON execution_runs(target_file, started_at DESC)
        """)

def save_assignment(
    line_number: int,
    variable_name: str,
    serialized_value: str,
) -> None:
    timestamp = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO variable_history (
                timestamp,
                line_number,
                variable_name,
                serialized_value
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                timestamp,
                line_number,
                variable_name,
                serialized_value,
            ),
        )

def save_runtime_state(
    line_number: int,
    source_line: str,
    locals_snapshot: str,
) -> None:

    timestamp = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:

        connection.execute(
            """
            INSERT INTO runtime_history(
                timestamp,
                line_number,
                source_line,
                locals_snapshot
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                timestamp,
                line_number,
                source_line,
                locals_snapshot,
            ),
        )

def get_runtime_states():

    with get_connection() as connection:

        cursor = connection.execute(
            """
            SELECT
                line_number,
                source_line,
                locals_snapshot
            FROM runtime_history
            ORDER BY id
            """
        )

        return cursor.fetchall()


def create_trace_run(target_file: str) -> str:
    """Start a trace run and return the identifier used by all of its events."""

    run_id = str(uuid.uuid4())
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO execution_runs (run_id, target_file, started_at)
            VALUES (?, ?, ?)
            """,
            (run_id, str(Path(target_file).resolve()), datetime.now(timezone.utc).isoformat()),
        )
    return run_id


def save_execution_delta(
    run_id: str,
    step_index: int,
    line_number: int,
    source_line: str,
    delta: dict[str, Any],
) -> None:
    """Persist one compact trace event; no full locals snapshot is stored."""

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO execution_deltas (
                run_id, step_index, timestamp, line_number, source_line, delta_json
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                step_index,
                datetime.now(timezone.utc).isoformat(),
                line_number,
                source_line,
                json.dumps(delta, separators=(",", ":"), ensure_ascii=False),
            ),
        )


def get_execution_events(
    target_file: str | None = None, run_id: str | None = None
) -> list[ExecutionEvent]:
    """Load one complete run, defaulting to the latest run for the target."""

    with get_connection() as connection:
        selected_run = run_id
        if selected_run is None:
            if target_file is None:
                row = connection.execute(
                    "SELECT run_id FROM execution_runs ORDER BY started_at DESC LIMIT 1"
                ).fetchone()
            else:
                row = connection.execute(
                    """
                    SELECT run_id FROM execution_runs
                    WHERE target_file = ?
                    ORDER BY started_at DESC LIMIT 1
                    """,
                    (str(Path(target_file).resolve()),),
                ).fetchone()
            if row is None:
                return []
            selected_run = row["run_id"]

        rows = connection.execute(
            """
            SELECT run_id, step_index, line_number, source_line, delta_json
            FROM execution_deltas
            WHERE run_id = ?
            ORDER BY step_index
            """,
            (selected_run,),
        ).fetchall()

    return [
        ExecutionEvent(
            run_id=row["run_id"],
            step_index=row["step_index"],
            line_number=row["line_number"],
            source_line=row["source_line"],
            delta=json.loads(row["delta_json"]),
        )
        for row in rows
    ]


