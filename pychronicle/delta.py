"""Delta creation and reconstruction helpers for execution snapshots.

The tracer stores ``repr`` values rather than live Python objects.  This makes
the history safe to persist in SQLite and lets it handle values such as open
files and custom objects that are not JSON serialisable.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def make_delta(
    previous: Mapping[str, str], current: Mapping[str, str]
) -> dict[str, Any]:
    """Return only the variables that changed from *previous* to *current*.

    ``set`` contains new or changed values. ``deleted`` contains names that
    disappeared from the frame.  Keeping deletion separate avoids confusing a
    real value represented by the string ``"None"`` with a deleted variable.
    """

    changed = {
        name: value
        for name, value in current.items()
        if previous.get(name) != value
    }
    deleted = sorted(set(previous) - set(current))
    return {"set": changed, "deleted": deleted}


def apply_delta(
    state: Mapping[str, str], delta: Mapping[str, Any]
) -> dict[str, str]:
    """Apply a stored delta and return a new reconstructed state."""

    reconstructed = dict(state)
    for name in delta.get("deleted", []):
        reconstructed.pop(name, None)
    for name, value in delta.get("set", {}).items():
        reconstructed[name] = value
    return reconstructed


def delta_is_empty(delta: Mapping[str, Any]) -> bool:
    """Whether a delta has no variable changes."""

    return not delta.get("set") and not delta.get("deleted")
