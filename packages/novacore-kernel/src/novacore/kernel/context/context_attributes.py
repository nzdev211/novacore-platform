from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any


def _freeze(value: Any, active: set[int]) -> Any:
    """Recursively convert supported containers into immutable containers."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, Mapping):
        object_id = id(value)
        if object_id in active:
            raise ValueError("Cyclic contextual attributes are not supported.")
        active.add(object_id)
        try:
            frozen: dict[str, Any] = {}
            for key, item in value.items():
                if not isinstance(key, str) or not key.strip():
                    raise ValueError("Context attribute keys must be non-empty strings.")
                frozen[key] = _freeze(item, active)
            return MappingProxyType(frozen)
        finally:
            active.remove(object_id)

    if isinstance(value, (list, tuple)):
        object_id = id(value)
        if object_id in active:
            raise ValueError("Cyclic contextual attributes are not supported.")
        active.add(object_id)
        try:
            return tuple(_freeze(item, active) for item in value)
        finally:
            active.remove(object_id)

    if isinstance(value, (set, frozenset)):
        object_id = id(value)
        if object_id in active:
            raise ValueError("Cyclic contextual attributes are not supported.")
        active.add(object_id)
        try:
            try:
                return frozenset(_freeze(item, active) for item in value)
            except TypeError as exc:
                raise TypeError("Set elements must become hashable immutable values.") from exc
        finally:
            active.remove(object_id)

    raise TypeError(f"Unsupported contextual attribute type: {type(value).__name__}")


def _hashable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return tuple(sorted((key, _hashable(item)) for key, item in value.items()))
    if isinstance(value, tuple):
        return tuple(_hashable(item) for item in value)
    if isinstance(value, frozenset):
        return frozenset(_hashable(item) for item in value)
    return value


@dataclass(frozen=True, eq=False)
class ContextAttributes:
    """Immutable generic metadata associated with a Context."""

    values: Mapping[str, object]

    def __post_init__(self) -> None:
        if not isinstance(self.values, Mapping):
            raise TypeError("ContextAttributes values must be a mapping.")
        object.__setattr__(self, "values", _freeze(self.values, set()))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ContextAttributes):
            return NotImplemented
        return self.values == other.values

    def __hash__(self) -> int:
        return hash(_hashable(self.values))

