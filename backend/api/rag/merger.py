from copy import deepcopy
from typing import Any, Optional


def merge(previous: Optional[Any], current: Any) -> Any:
    if previous is None:
        return current

    merged = deepcopy(previous)
    merge_objects(merged, current)
    return merged


def merge_objects(old: Any, new: Any) -> None:
    for key, value in vars(new).items():
        if hasattr(value, "__dict__"):
            merge_objects(
                getattr(old, key),
                value,
            )
        elif value is not None:
            setattr(old, key, value)