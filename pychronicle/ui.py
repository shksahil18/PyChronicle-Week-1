from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Static
from pychronicle.storage import get_runtime_states


class CodePane(Static):
    pass


class TimelinePane(Static):
    pass


class SliderPane(Static):
    pass


class PyChronicleUI(App):

    TITLE = "PyChronicle"
    SUB_TITLE = "Week 2 - Time Travel Debugger"

    CSS = """

    Screen{
        layout:vertical;
    }

    Horizontal{
        height:1fr;
    }

    CodePane{
        width:70%;
        border:round green;
        padding:1;
    }

    Vertical{
        width:30%;
    }

    TimelinePane{
        height:1fr;
        border:round cyan;
        padding:1;
    }

    SliderPane{
        height:5;
        border:round yellow;
        padding:1;
    }

    """

    def __init__(self,target_file):

        super().__init__()

        self.target_file=target_file

    def load_source(self):

        path=Path(self.target_file)

        lines=path.read_text().splitlines()

        output=[]

        for i,line in enumerate(lines,start=1):

            output.append(f"{i:>3} │ {line}")

        return "\n".join(output)

    def load_timeline(self):
        states = get_runtime_states()
        if not states:
            return "No runtime states found."
        output = [
            "Execution Timeline",
            "",
        ]
        for state in states:
            line_number = state[0]
            source_line = state[1]
            output.append(
                f"✓ Line {line_number} : {source_line}"
            )
        return "\n".join(output)
    

    def compose(self)->ComposeResult:

        yield Header(show_clock=True)

        with Horizontal():

            yield CodePane(
                self.load_source(),
                id="code"
            )

            with Vertical():

                yield TimelinePane(
                    self.load_timeline(),
                    id="timeline",
               )             

                yield SliderPane(
"""
Timeline

0% ─────────────────────────────── 100%

                ▲

(Currently Placeholder)

Week 3
will use a real slider.
"""
                )

        yield Footer()