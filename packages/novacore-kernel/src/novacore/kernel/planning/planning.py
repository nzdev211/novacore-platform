from dataclasses import dataclass

from novacore.kernel.identity import ActivityId, ObjectiveId, PlanningId


@dataclass(frozen=True, eq=False)
class Planning:
    """Immutable planning record scoped to an Activity and Objective."""

    id: PlanningId
    activity_id: ActivityId
    objective_id: ObjectiveId
    description: str

    def __post_init__(self) -> None:
        if not isinstance(self.id, PlanningId):
            raise TypeError("Planning id must be a PlanningId.")
        if not isinstance(self.activity_id, ActivityId):
            raise TypeError("Planning activity_id must be an ActivityId.")
        if not isinstance(self.objective_id, ObjectiveId):
            raise TypeError("Planning objective_id must be an ObjectiveId.")
        if not isinstance(self.description, str):
            raise TypeError("Planning description must be a string.")
        if not self.description.strip():
            raise ValueError("Planning description cannot be empty or whitespace-only.")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Planning):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

