
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any


def _freeze(value: Any, active: set[int]) -> Any:
    """
    Recursively convert supported values into immutable equivalents.
    """

    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, Mapping):
        object_id = id(value)

        if object_id in active:
            raise ValueError("Cyclic contextual attributes are not supported.")

        active.add(object_id)

        try:
            frozen = {}

            for key, item in value.items():
                if not isinstance(key, str) or not key.strip():
                    raise ValueError(
                        "Context attribute keys must be non-empty strings."
                    )

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
            frozen_items = (_freeze(item, active) for item in value)

            try:
                return frozenset(frozen_items)
            except TypeError as exc:
                raise TypeError(
                    "Set elements must become hashable immutable values."
                ) from exc
        finally:
            active.remove(object_id)

    raise TypeError(
        f"Unsupported contextual attribute type: {type(value).__name__}"
    )


def _hashable(value: Any) -> Any:
    """
    Convert frozen values into stable hashable representations.
    """

    if isinstance(value, Mapping):
        return tuple(
            sorted(
                (key, _hashable(item))
                for key, item in value.items()
            )
        )

    if isinstance(value, tuple):
        return tuple(_hashable(item) for item in value)

    if isinstance(value, frozenset):
        return frozenset(_hashable(item) for item in value)

    return value


@dataclass(frozen=True, eq=False)
class ContextAttributes:
    """
    Represents immutable, generic contextual attributes.

    Supports scalar values and nested collections.
    Mutable collections are recursively converted into
    immutable equivalents.
    """

    values: Mapping[str, object]

    def __post_init__(self) -> None:
        if not isinstance(self.values, Mapping):
            raise TypeError(
                "ContextAttributes values must be a mapping."
            )

        frozen_values = _freeze(self.values, set())

        object.__setattr__(self, "values", frozen_values)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ContextAttributes):
            return NotImplemented

        return dict(self.values) == dict(other.values)

    def __hash__(self) -> int:
        return hash(_hashable(self.values))

