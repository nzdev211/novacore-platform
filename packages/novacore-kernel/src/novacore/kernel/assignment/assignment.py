from dataclasses import dataclass

from novacore.kernel.identity import AssignmentId, WorkId, WorkerId


@dataclass(frozen=True, eq=False)
class Assignment:
    """Immutable allocation of a Work item to a Worker."""

    id: AssignmentId
    work_id: WorkId
    worker_id: WorkerId

    def __post_init__(self) -> None:
        if not isinstance(self.id, AssignmentId):
            raise TypeError("Assignment id must be an AssignmentId.")
        if not isinstance(self.work_id, WorkId):
            raise TypeError("Assignment work_id must be a WorkId.")
        if not isinstance(self.worker_id, WorkerId):
            raise TypeError("Assignment worker_id must be a WorkerId.")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Assignment):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

