from typing import TypeVar

import model

T = TypeVar('T')
Named = TypeVar('Named', model.Color, model.Theme)


def chunk(arr: list[T], chunksize: int) -> list[list[T]]:
    """Split a list into a list of lists of a specific size"""
    return [arr[i: i + chunksize] for i in range(0, len(arr), chunksize)]


def ellipsize(text: str, maxsize: int = 64) -> str:
    """Shrink a string to a certain size and ellipsize it"""
    if len(text) < maxsize:
        return text
    return text[:maxsize] + "..."


def find_by_name(name: str, items: list[Named]) -> Named | None:
    """Find something in a list by name attribute."""
    return next((item for item in items if item.name.lower() == name.lower()), None)
