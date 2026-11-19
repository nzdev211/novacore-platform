
from dataclasses import dataclass

from novacore.kernel.identity import WorkerId, CapabilityId


@dataclass(frozen=True, eq=False)
class Worker:
    """
    Represents an execution resource within Novacore.

    A Worker can provide multiple capabilities.
    Worker references capabilities through CapabilityId.
    """

    id: WorkerId
    capability_ids: tuple[CapabilityId, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.id, WorkerId):
            raise TypeError("Worker id must be a WorkerId.")

        if not isinstance(self.capability_ids, tuple):
            raise TypeError(
                "Worker capability_ids must be a tuple."
            )

        if not all(
            isinstance(capability_id, CapabilityId)
            for capability_id in self.capability_ids
        ):
            raise TypeError(
                "Every capability reference must be a CapabilityId."
            )

        if len(self.capability_ids) != len(set(self.capability_ids)):
            raise ValueError(
                "Worker cannot contain duplicate CapabilityIds."
            )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Worker):
            return NotImplemented

        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
