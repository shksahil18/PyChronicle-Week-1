"""
PyChronicle Flask Web Application.

Provides a browser-based interface over the existing
PyChronicle tracer, SQLite storage, delta compression,
and timeline reconstruction system.
"""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlencode

from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug.utils import secure_filename

from pychronicle.storage import (
    create_table,
    get_connection,
    get_execution_events,
)
from pychronicle.timeline import ExecutionTimeline
from pychronicle.tracer import ExecutionTracer


PROJECT_ROOT = Path(__file__).resolve().parent.parent

UPLOAD_DIR = PROJECT_ROOT / "data" / "web_targets"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static",
)


def discover_targets() -> list[str]:
    """
    Find Python files available in the project root.
    """

    targets = []

    for path in PROJECT_ROOT.glob("*.py"):

        if path.name.startswith("_"):
            continue

        targets.append(path.name)

    return sorted(targets)


def resolve_project_target(
    target_name: str,
) -> Path:
    """
    Resolve a target Python file inside the project root.

    This prevents the browser form from accessing arbitrary
    files outside the project directory.
    """

    if not target_name:
        target_name = "sample_target.py"

    candidate = (
        PROJECT_ROOT / target_name
    ).resolve()

    try:

        candidate.relative_to(
            PROJECT_ROOT
        )

    except ValueError as error:

        raise ValueError(
            "Target file must be inside "
            "the PyChronicle project directory."
        ) from error

    if not candidate.is_file():

        raise ValueError(
            f"Target file not found: {candidate}"
        )

    if candidate.suffix.lower() != ".py":

        raise ValueError(
            "Only Python .py files are supported."
        )

    return candidate


def get_run_target(
    run_id: str,
) -> Path | None:
    """
    Get the target file associated with a trace run.
    """

    with get_connection() as connection:

        row = connection.execute(
            """
            SELECT target_file
            FROM execution_runs
            WHERE run_id = ?
            """,
            (run_id,),
        ).fetchone()

    if row is None:
        return None

    return Path(row["target_file"])


@app.get("/")
def index():
    """
    Main browser dashboard.
    """

    return render_template(
        "index.html",
        targets=discover_targets(),
        default_target="sample_target.py",
        error=None,
    )


@app.post("/run")
def run_trace():
    """
    Execute a target Python script through the existing
    PyChronicle tracer.
    """

    try:

        uploaded_file = request.files.get(
            "script_file"
        )

        # -------------------------------------------------
        # Option 1: Browser file upload
        # -------------------------------------------------

        if (
            uploaded_file
            and uploaded_file.filename
        ):

            filename = secure_filename(
                uploaded_file.filename
            )

            if not filename.lower().endswith(
                ".py"
            ):

                raise ValueError(
                    "Only .py files can be uploaded."
                )

            target_file = (
                UPLOAD_DIR / filename
            )

            uploaded_file.save(
                target_file
            )

        # -------------------------------------------------
        # Option 2: Existing project file
        # -------------------------------------------------

        else:

            target_file = resolve_project_target(
                request.form.get(
                    "target_path",
                    "sample_target.py",
                )
            )

        # -------------------------------------------------
        # Watch Variables
        # -------------------------------------------------

        watch_text = request.form.get(
            "watch_variables",
            "",
        )

        watch_variables = [
            name.strip()
            for name in watch_text.split(",")
            if name.strip()
        ]

        # -------------------------------------------------
        # Initialize database
        # -------------------------------------------------

        create_table()

        # -------------------------------------------------
        # Run PyChronicle tracer
        # -------------------------------------------------

        tracer = ExecutionTracer(
            target_file
        )

        run_id = tracer.run(
            target_file
        )

        if tracer.step_index == 0:

            raise ValueError(
                "The target script produced "
                "no trace events."
            )

        # -------------------------------------------------
        # Redirect to debugger
        # -------------------------------------------------

        query = urlencode(
            [
                ("watch", name)
                for name in watch_variables
            ]
        )

        debugger_url = url_for(
            "debugger",
            run_id=run_id,
        )

        if query:

            debugger_url += (
                "?" + query
            )

        return redirect(
            debugger_url
        )

    except Exception as error:

        return render_template(
            "index.html",
            targets=discover_targets(),
            default_target="sample_target.py",
            error=str(error),
        ), 400


@app.get("/debug/<run_id>")
def debugger(
    run_id: str,
):
    """
    Browser debugger screen for a stored execution run.
    """

    target_file = get_run_target(
        run_id
    )

    if (
        target_file is None
        or not target_file.is_file()
    ):

        return (
            "Execution run not found.",
            404,
        )

    events = get_execution_events(
        run_id=run_id
    )

    timeline = (
        ExecutionTimeline.from_database(
            run_id=run_id
        )
    )

    source_lines = (
        target_file
        .read_text(
            encoding="utf-8"
        )
        .splitlines()
    )

    # -----------------------------------------------------
    # Timeline metadata
    # -----------------------------------------------------

    event_data = []

    for event in events:

        changed = list(
            event.delta.get(
                "set",
                {},
            ).keys()
        )

        deleted = list(
            event.delta.get(
                "deleted",
                []
            )
        )

        event_data.append(
            {
                "step": event.step_index,
                "line": event.line_number,
                "source": event.source_line,
                "changed": changed,
                "deleted": deleted,
            }
        )

    # -----------------------------------------------------
    # Watch Variables
    # -----------------------------------------------------

    watch_variables = request.args.getlist(
        "watch"
    )

    watch_history = []

    for index, point in enumerate(
        timeline.points
    ):

        values = {}

        for name in watch_variables:

            values[name] = point.state.get(
                name,
                "<not defined>",
            )

        watch_history.append(
            {
                "step": index,
                "line": point.event.line_number,
                "values": values,
            }
        )

    return render_template(
        "debugger.html",
        run_id=run_id,
        target_file=str(target_file),
        source_lines=source_lines,
        events=event_data,
        watch_variables=watch_variables,
        watch_history=watch_history,
        total_steps=len(timeline),
    )


@app.get(
    "/api/runs/<run_id>/step/<int:step>"
)
def step_state(
    run_id: str,
    step: int,
):
    """
    Return the reconstructed state for one
    historical execution step.
    """

    timeline = (
        ExecutionTimeline.from_database(
            run_id=run_id
        )
    )

    if not timeline:

        return jsonify(
            {
                "error":
                "No execution history found."
            }
        ), 404

    if (
        step < 0
        or step >= len(timeline)
    ):

        return jsonify(
            {
                "error":
                "Invalid timeline step."
            }
        ), 404

    point = timeline.at(
        step
    )

    return jsonify(
        {
            "step": step,
            "line_number":
                point.event.line_number,
            "source_line":
                point.event.source_line,
            "delta":
                point.event.delta,
            "state":
                point.state,
        }
    )


@app.get("/health")
def health():
    """
    Simple health-check endpoint.
    """

    return jsonify(
        {
            "status": "ok",
            "application":
                "PyChronicle Flask Web",
        }
    )


if __name__ == "__main__":

    create_table()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
        use_reloader=False,
        threaded=False,
    )