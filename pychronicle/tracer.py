import json
import sys
import linecache
from pathlib import Path

from pychronicle.storage import save_runtime_state


class ExecutionTracer:
    """
    Simple execution tracer using sys.settrace().
    """

    def __init__(self, target_file):
        self.target_file = Path(target_file).resolve()

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

        print("\n" + "=" * 40)

        print(f"File : {current_file.name}")
        print(f"Line : {line_number}")

        print("\nSource:")

        print(source_line)

        print("\nVariables:")

        snapshot = {}

        if frame.f_locals:
            for name, value in frame.f_locals.items():
                print(f"{name} = {repr(value)}")
                snapshot[name] = repr(value)
        else:
            print("No local variables")

        serialized = json.dumps(snapshot)

        save_runtime_state(
            line_number,
            source_line,
            serialized,
        )

        return self.trace

    def run(self, script_path):

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

        sys.settrace(self.trace)

        try:

            exec(compiled, namespace)

        finally:

            sys.settrace(None)