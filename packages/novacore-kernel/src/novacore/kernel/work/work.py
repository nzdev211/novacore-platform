from dataclasses import dataclass

from novacore.kernel.identity import ActivityId, PlanningId, WorkId


@dataclass(frozen=True, eq=False)
class Work:
    """Immutable unit of work belonging to an Activity."""

    id: WorkId
    activity_id: ActivityId
    description: str
    planning_id: PlanningId | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.id, WorkId):
            raise TypeError("Work id must be a WorkId.")
        if not isinstance(self.activity_id, ActivityId):
            raise TypeError("Work activity_id must be an ActivityId.")
        if not isinstance(self.description, str):
            raise TypeError("Work description must be a string.")
        if not self.description.strip():
            raise ValueError("Work description cannot be empty or whitespace-only.")
        if self.planning_id is not None and not isinstance(self.planning_id, PlanningId):
            raise TypeError("Work planning_id must be a PlanningId or None.")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Work):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
