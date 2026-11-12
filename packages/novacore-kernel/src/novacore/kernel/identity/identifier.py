
from dataclasses import dataclass


@dataclass(frozen=True, eq=False, repr=False)
class Identifier:
    """
    Abstract domain base type for Novacore identifiers.

    Identifier provides a common immutable identity representation.
    Concrete identifier types inherit its value and behavior.

    Identity generation is handled externally.
    """

    value: str

    def __new__(cls, *args: object, **kwargs: object):
        if cls is Identifier:
            raise TypeError(
                "Identifier is an abstract domain type "
                "and cannot be instantiated directly."
            )

        return super().__new__(cls)

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise TypeError("Identifier value must be a string.")

        if not self.value or not self.value.strip():
            raise ValueError(
                "Identifier value cannot be empty or whitespace-only."
            )

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Identifier):
            return NotImplemented

        return (
            type(self) is type(other)
            and self.value == other.value
        )

    def __hash__(self) -> int:
        return hash((type(self), self.value))
