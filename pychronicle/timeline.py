"""Reconstruct a trace run from its compact delta events."""

from __future__ import annotations

from dataclasses import dataclass

from pychronicle.delta import apply_delta
from pychronicle.storage import ExecutionEvent, get_execution_events


@dataclass(frozen=True)
class TimelinePoint:
    """One historical point, with its state rebuilt from prior deltas."""

    event: ExecutionEvent
    state: dict[str, str]


class ExecutionTimeline:
    """An indexed, read-only execution history for the terminal UI."""

    def __init__(self, points: list[TimelinePoint]):
        self._points = points

    @classmethod
    def from_database(
        cls, target_file: str | None = None, run_id: str | None = None
    ) -> "ExecutionTimeline":
        state: dict[str, str] = {}
        points: list[TimelinePoint] = []
        for event in get_execution_events(target_file=target_file, run_id=run_id):
            state = apply_delta(state, event.delta)
            points.append(TimelinePoint(event=event, state=state))
        return cls(points)

    def __len__(self) -> int:
        return len(self._points)

    def at(self, index: int) -> TimelinePoint:
        if not self._points:
            raise IndexError("The timeline has no execution events.")
        return self._points[max(0, min(index, len(self._points) - 1))]

    @property
    def points(self) -> tuple[TimelinePoint, ...]:
        return tuple(self._points)
