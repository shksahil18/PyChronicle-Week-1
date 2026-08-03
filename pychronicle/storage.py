import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "pychronicle.db"


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


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



