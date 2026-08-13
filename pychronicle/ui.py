"""
Interactive Textual UI for PyChronicle Week 4.

Week 4 additions:
- Watch Variables
- Watch history across timeline steps
- CLI-selected watched variables
- Historical line highlighting
- Timeline scrubbing
"""

from __future__ import annotations

from pathlib import Path

from rich.text import Text

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.events import Click
from textual.widgets import Footer, Header, Static

from pychronicle.timeline import ExecutionTimeline


class CodePane(Static):
    """Displays source code with the selected line highlighted."""


class TimelinePane(Static):
    """Displays historical execution events."""


class VariablesPane(Static):
    """Displays all reconstructed variables at the selected point."""


class WatchPane(Static):
    """Displays user-selected variables across execution history."""


class TimelineSlider(Static):
    """
    Dependency-free timeline slider.

    This avoids relying on Textual's Slider widget.
    """

    can_focus = True

    def __init__(
        self,
        maximum: int,
        **kwargs,
    ) -> None:

        super().__init__(**kwargs)

        self.maximum = max(0, maximum)
        self.position = 0

    def set_position(self, position: int) -> None:

        self.position = max(
            0,
            min(position, self.maximum),
        )

        self.refresh()

    def render(self) -> Text:

        track_width = 36

        if self.maximum:

            marker = round(
                (self.position / self.maximum)
                * (track_width - 1)
            )

        else:

            marker = 0

        track = ["-"] * track_width

        track[marker] = "O"

        return Text(
            (
                f"Step {self.position + 1} / "
                f"{self.maximum + 1}  "
                f"[{''.join(track)}]  "
                f"Left/Right: scrub | "
                f"Home/End: jump"
            ),
            style="bold yellow",
        )

    def on_click(self, event: Click) -> None:
        """Jump to an approximate timeline position."""

        if not self.maximum:
            return

        width = max(
            1,
            self.size.width - 1,
        )

        position = round(
            (event.x / width)
            * self.maximum
        )

        self.app.set_timeline_position(position)


class PyChronicleUI(App):
    """
    Main PyChronicle Week 4 debugger interface.
    """

    TITLE = "PyChronicle"

    SUB_TITLE = (
        "Week 4 - CLI + Watch Variables"
    )

    BINDINGS = [
        (
            "left",
            "previous",
            "Previous step",
        ),
        (
            "right",
            "next",
            "Next step",
        ),
        (
            "home",
            "first",
            "First step",
        ),
        (
            "end",
            "last",
            "Last step",
        ),
    ]

    CSS = """

    Screen {
        layout: vertical;
    }

    Horizontal {
        height: 1fr;
    }

    CodePane {
        width: 55%;
        border: round green;
        padding: 1;
        overflow: auto;
    }

    Vertical {
        width: 45%;
    }

    TimelinePane {
        height: 30%;
        border: round cyan;
        padding: 1;
        overflow: auto;
    }

    VariablesPane {
        height: 25%;
        border: round magenta;
        padding: 1;
        overflow: auto;
    }

    WatchPane {
        height: 45%;
        border: round yellow;
        padding: 1;
        overflow: auto;
    }

    TimelineSlider {
        height: 3;
        border: round yellow;
        padding: 1;
    }

    """

    def __init__(
        self,
        target_file: str,
        run_id: str | None = None,
        watch_variables: list[str] | None = None,
    ) -> None:

        super().__init__()

        self.target_file = Path(
            target_file
        ).resolve()

        self.run_id = run_id

        self.watch_variables = (
            watch_variables or []
        )

        self.source_lines = (
            self.target_file
            .read_text(
                encoding="utf-8"
            )
            .splitlines()
        )

        self.timeline = (
            ExecutionTimeline.from_database(
                target_file=str(
                    self.target_file
                ),
                run_id=self.run_id,
            )
        )

        self.position = max(
            0,
            len(self.timeline) - 1,
        )

    def compose(self) -> ComposeResult:

        yield Header(
            show_clock=True
        )

        with Horizontal():

            yield CodePane(
                id="code"
            )

            with Vertical():

                yield TimelinePane(
                    id="timeline"
                )

                yield VariablesPane(
                    id="variables"
                )

                yield WatchPane(
                    id="watch"
                )

        yield TimelineSlider(
            maximum=max(
                0,
                len(self.timeline) - 1,
            ),
            id="slider",
        )

        yield Footer()

    def on_mount(self) -> None:

        self.refresh_panels()

        self.query_one(
            TimelineSlider
        ).focus()

    def render_code(
        self,
        highlighted_line: int | None,
    ) -> Text:

        output = Text()

        for number, line in enumerate(
            self.source_lines,
            start=1,
        ):

            style = ""

            if number == highlighted_line:

                style = (
                    "bold black on yellow"
                )

            output.append(
                f"{number:>4} | {line}\n",
                style=style,
            )

        return output

    def render_timeline(self) -> Text:

        if not self.timeline:

            return Text(
                "No delta trace found. "
                "Run the tracer first.",
                style="yellow",
            )

        output = Text(
            "Execution Timeline\n\n",
            style="bold cyan",
        )

        start = max(
            0,
            self.position - 5,
        )

        stop = min(
            len(self.timeline),
            self.position + 6,
        )

        for index in range(
            start,
            stop,
        ):

            point = self.timeline.at(
                index
            )

            event = point.event

            marker = (
                ">"
                if index == self.position
                else " "
            )

            changed = ", ".join(
                event.delta.get(
                    "set",
                    {},
                )
            )

            if not changed:

                changed = (
                    "no variable change"
                )

            removed = event.delta.get(
                "deleted",
                [],
            )

            if removed:

                changed += (
                    "; deleted: "
                    + ", ".join(removed)
                )

            output.append(
                (
                    f"{marker} "
                    f"{index + 1:>3}. "
                    f"line "
                    f"{event.line_number:<3} "
                    f"{changed}\n"
                ),
                style=(
                    "bold white on blue"
                    if index == self.position
                    else ""
                ),
            )

            output.append(
                f"      {event.source_line}\n"
            )

        return output

    def render_variables(self) -> Text:

        if not self.timeline:

            return Text(
                "Reconstructed Variables\n\n"
                "No state available.",
                style="yellow",
            )

        point = self.timeline.at(
            self.position
        )

        output = Text(
            (
                f"Variables at step "
                f"{self.position + 1}\n\n"
            ),
            style="bold magenta",
        )

        if not point.state:

            output.append(
                "No local variables"
            )

        else:

            for name, value in sorted(
                point.state.items()
            ):

                output.append(
                    f"{name} = {value}\n"
                )

        return output

    def render_watch(self) -> Text:

        output = Text(
            "Watch Variables\n\n",
            style="bold yellow",
        )

        if not self.watch_variables:

            output.append(
                "No variables selected.\n\n"
            )

            output.append(
                "Use:\n"
                "pychronicle run "
                "sample_target.py "
                "--watch x "
                "--watch total"
            )

            return output

        if not self.timeline:

            output.append(
                "No execution history."
            )

            return output

        current = self.timeline.at(
            self.position
        )

        output.append(
            f"Current step: "
            f"{self.position + 1}\n\n"
        )

        for name in self.watch_variables:

            value = current.state.get(
                name,
                "<not defined>",
            )

            output.append(
                f"{name:<18} = {value}\n"
            )

        output.append(
            "\nHistory\n"
        )

        start = max(
            0,
            self.position - 4,
        )

        stop = min(
            len(self.timeline),
            self.position + 1,
        )

        for index in range(
            start,
            stop,
        ):

            point = self.timeline.at(
                index
            )

            values = []

            for name in self.watch_variables:

                value = point.state.get(
                    name,
                    "-",
                )

                values.append(
                    f"{name}={value}"
                )

            output.append(
                f"Step {index + 1:<3} "
                + " | ".join(values)
                + "\n"
            )

        return output

    def refresh_panels(self) -> None:

        highlighted_line = None

        if self.timeline:

            highlighted_line = (
                self.timeline
                .at(self.position)
                .event
                .line_number
            )

        self.query_one(
            CodePane
        ).update(
            self.render_code(
                highlighted_line
            )
        )

        self.query_one(
            TimelinePane
        ).update(
            self.render_timeline()
        )

        self.query_one(
            VariablesPane
        ).update(
            self.render_variables()
        )

        self.query_one(
            WatchPane
        ).update(
            self.render_watch()
        )

        self.query_one(
            TimelineSlider
        ).set_position(
            self.position
        )

    def set_timeline_position(
        self,
        position: int,
    ) -> None:

        if not self.timeline:

            return

        self.position = max(
            0,
            min(
                position,
                len(self.timeline) - 1,
            ),
        )

        self.refresh_panels()

    def action_previous(self) -> None:

        self.set_timeline_position(
            self.position - 1
        )

    def action_next(self) -> None:

        self.set_timeline_position(
            self.position + 1
        )

    def action_first(self) -> None:

        self.set_timeline_position(0)

    def action_last(self) -> None:

        self.set_timeline_position(
            len(self.timeline) - 1
        )
