from dataclasses import dataclass

from novacore.kernel.identity import CapabilityId, WorkerId


@dataclass(frozen=True, eq=False)
class Worker:
    """Immutable execution resource with references to its capabilities."""

    id: WorkerId
    capability_ids: tuple[CapabilityId, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.id, WorkerId):
            raise TypeError("Worker id must be a WorkerId.")
        if not isinstance(self.capability_ids, tuple):
            raise TypeError("Worker capability_ids must be a tuple.")
        if any(not isinstance(item, CapabilityId) for item in self.capability_ids):
            raise TypeError("Every Worker capability reference must be a CapabilityId.")
        if len(set(self.capability_ids)) != len(self.capability_ids):
            raise ValueError("Worker capability_ids cannot contain duplicates.")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Worker):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

