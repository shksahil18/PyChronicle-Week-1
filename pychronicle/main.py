"""Command-line entry point for PyChronicle."""

from __future__ import annotations

import argparse
from pathlib import Path

from pychronicle.ast_parser import find_assignments
from pychronicle.storage import create_table, save_assignment
from pychronicle.tracer import ExecutionTracer
from pychronicle.ui import PyChronicleUI


DEFAULT_TARGET = "sample_target.py"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Trace a Python script with PyChronicle.")
    parser.add_argument("target", nargs="?", default=DEFAULT_TARGET, help="Python script to trace")
    parser.add_argument(
        "--no-ui", action="store_true", help="Save the trace but do not launch Textual"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    target_file = Path(args.target).resolve()
    if not target_file.is_file():
        raise FileNotFoundError(f"Target file not found: {target_file}")

    create_table()

    assignments = find_assignments(target_file)
    for assignment in assignments:
        save_assignment(
            assignment["line_number"],
            assignment["variable_name"],
            assignment["serialized_value"],
        )

    tracer = ExecutionTracer(target_file)
    run_id = tracer.run(target_file)
    print(f"Saved {tracer.step_index} delta events for run {run_id}.")

    if not args.no_ui:
        PyChronicleUI(str(target_file)).run()


if __name__ == "__main__":
    main()
