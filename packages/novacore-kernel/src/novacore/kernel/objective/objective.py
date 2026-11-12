from dataclasses import dataclass

from novacore.kernel.identity import ObjectiveId


@dataclass(frozen=True, eq=False)
class Objective:
    """Represents a desired outcome for an Activity."""

    id: ObjectiveId
    description: str

    def __post_init__(self) -> None:
        if not isinstance(self.id, ObjectiveId):
            raise TypeError("Objective id must be an ObjectiveId.")

        if not isinstance(self.description, str):
            raise TypeError("Objective description must be a string.")

        if not self.description.strip():
            raise ValueError(
                "Objective description cannot be empty or whitespace-only."
            )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Objective):
            return NotImplemented

        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
