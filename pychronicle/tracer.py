import sys
import linecache
from pathlib import Path

from pychronicle.delta import make_delta
from pychronicle.storage import create_trace_run, save_execution_delta


class ExecutionTracer:
    """
    Simple execution tracer using sys.settrace().
    """

    def __init__(self, target_file):
        self.target_file = Path(target_file).resolve()
        self.previous_snapshot: dict[str, str] = {}
        self.run_id: str | None = None
        self.step_index = 0

    def trace(self, frame, event, arg):

        # Ignore everything except executed lines
        if event != "line":
            return self.trace

        current_file = Path(frame.f_code.co_filename).resolve()

        # Trace only our target file
        if current_file != self.target_file:
            return self.trace

        line_number = frame.f_lineno

        source_line = linecache.getline(
            str(current_file),
            line_number
        ).rstrip()

        snapshot = {
            name: repr(value)
            for name, value in frame.f_locals.items()
            if not name.startswith("__")
        }
        delta = make_delta(self.previous_snapshot, snapshot)
        if self.run_id is None:
            raise RuntimeError("Trace run was not initialised.")
        save_execution_delta(
            self.run_id, self.step_index, line_number, source_line, delta
        )
        self.previous_snapshot = snapshot
        self.step_index += 1

        return self.trace

    def run(self, script_path) -> str:

        script_path = Path(script_path).resolve()

        code = script_path.read_text(encoding="utf-8")

        compiled = compile(
            code,
            str(script_path),
            "exec"
        )

        namespace = {
            "__name__": "__main__",
            "__file__": str(script_path)
        }

        self.previous_snapshot = {}
        self.step_index = 0
        self.run_id = create_trace_run(str(script_path))

        sys.settrace(self.trace)

        try:

            exec(compiled, namespace)

        finally:

            sys.settrace(None)

        return self.run_id
