"""
PyChronicle Week 4 CLI.

Provides commands such as:

    pychronicle run sample_target.py

and:

    pychronicle run sample_target.py --watch x --watch total
"""

from __future__ import annotations

from pathlib import Path

import click

from pychronicle.storage import create_table
from pychronicle.tracer import ExecutionTracer


@click.group()
def cli() -> None:
    """PyChronicle - AST-powered time-travel debugger."""
    pass


@cli.command()
@click.argument(
    "script",
    type=click.Path(
        exists=True,
        dir_okay=False,
        readable=True,
        path_type=Path,
    ),
)
@click.option(
    "--watch",
    "watch_variables",
    multiple=True,
    help="Variable to monitor in the time-scrubbing UI. Can be used multiple times.",
)
@click.option(
    "--no-ui",
    is_flag=True,
    help="Run the tracer without launching the Textual UI.",
)
def run(
    script: Path,
    watch_variables: tuple[str, ...],
    no_ui: bool,
) -> None:
    """
    Trace a Python SCRIPT and optionally open the debugger UI.

    Example:

        pychronicle run sample_target.py

    Watch selected variables:

        pychronicle run sample_target.py --watch x --watch total
    """

    target_file = script.resolve()

    click.echo("=" * 60)
    click.echo("PyChronicle - Week 4")
    click.echo("CLI Time-Travel Debugger")
    click.echo("=" * 60)

    click.echo(f"\nTarget: {target_file}")

    if watch_variables:
        click.echo(
            "Watch variables: "
            + ", ".join(watch_variables)
        )
    else:
        click.echo("Watch variables: none")

    create_table()

    click.echo("\nStarting execution trace...")

    tracer = ExecutionTracer(target_file)

    try:
        run_id = tracer.run(target_file)

    except Exception as error:
        raise click.ClickException(
            f"Execution failed: {error}"
        ) from error

    click.echo(
        f"Trace completed successfully."
    )

    click.echo(
        f"Run ID: {run_id}"
    )

    click.echo(
        f"Recorded events: {tracer.step_index}"
    )

    if no_ui:
        click.echo(
            "\nUI disabled with --no-ui."
        )
        return

    click.echo(
        "\nLaunching PyChronicle TUI..."
    )

    from pychronicle.ui import PyChronicleUI

    PyChronicleUI(
        str(target_file),
        run_id=run_id,
        watch_variables=list(watch_variables),
    ).run()


@cli.command()
def version() -> None:
    """Show the PyChronicle version."""

    click.echo("PyChronicle 0.4.0")


if __name__ == "__main__":
    cli()