import sqlite3
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



# import sqlite3
# from pathlib import Path
# from datetime import datetime

# BASE_DIR = Path(__file__).resolve().parent.parent
# DATA_DIR = BASE_DIR / "data"
# DATA_DIR.mkdir(exist_ok=True)

# DB_PATH = DATA_DIR / "pychronicle.db"


# def create_table():
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()

#     cursor.execute("""
#     CREATE TABLE IF NOT EXISTS variable_history (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         timestamp TEXT NOT NULL,
#         line_number INTEGER NOT NULL,
#         variable_name TEXT NOT NULL,
#         serialized_value TEXT
#     )
#     """)

#     conn.commit()
#     conn.close()


# def save_assignment(line_number, variable_name, serialized_value):
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()

#     cursor.execute("""
#     INSERT INTO variable_history
#     (timestamp, line_number, variable_name, serialized_value)
#     VALUES (?, ?, ?, ?)
#     """, (
#         datetime.now().isoformat(),
#         line_number,
#         variable_name,
#         serialized_value
#     ))

#     conn.commit()
#     conn.close()