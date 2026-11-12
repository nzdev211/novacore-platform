
from dataclasses import dataclass

from novacore.kernel.identity import (
    ExecutionId,
    AssignmentId,
)


@dataclass(frozen=True, eq=False)
class Execution:
    """
    Represents an individual execution attempt in Novacore.

    Execution references the Assignment associated with
    the attempt.

    It does not perform orchestration or maintain runtime state.
    """

    id: ExecutionId
    assignment_id: AssignmentId

    def __post_init__(self) -> None:
        if not isinstance(self.id, ExecutionId):
            raise TypeError(
                "Execution id must be an ExecutionId."
            )

        if not isinstance(self.assignment_id, AssignmentId):
            raise TypeError(
                "Execution assignment_id must be an AssignmentId."
            )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Execution):
            return NotImplemented

        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

