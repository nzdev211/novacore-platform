
from dataclasses import dataclass

from novacore.kernel.identity import CapabilityId


@dataclass(frozen=True, eq=False)
class Capability:
    """
    Represents a descriptive capability within Novacore.

    Capability describes what an execution resource can do.
    It does not define how that capability is implemented.
    """

    id: CapabilityId
    name: str
    description: str

    def __post_init__(self) -> None:
        if not isinstance(self.id, CapabilityId):
            raise TypeError(
                "Capability id must be a CapabilityId."
            )

        if not isinstance(self.name, str):
            raise TypeError("Capability name must be a string.")

        if not self.name.strip():
            raise ValueError(
                "Capability name cannot be empty or whitespace-only."
            )

        if not isinstance(self.description, str):
            raise TypeError(
                "Capability description must be a string."
            )

        if not self.description.strip():
            raise ValueError(
                "Capability description cannot be empty "
                "or whitespace-only."
            )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Capability):
            return NotImplemented

        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
