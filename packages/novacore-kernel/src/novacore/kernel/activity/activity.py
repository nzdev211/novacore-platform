
from dataclasses import dataclass
from datetime import datetime

from novacore.kernel.identity import (
    ActivityId,
    ContextId,
    ObjectiveId,
)

from .activity_status import ActivityStatus


@dataclass(frozen=True, eq=False)
class Activity:
    """
    Represents a business effort within Novacore.

    Activity organizes related domain work through references
    to other domain identities.
    """

    id: ActivityId
    context_id: ContextId
    objective_id: ObjectiveId | None = None
    status: ActivityStatus
    created_at: datetime
    updated_at: datetime
    request_id: RequestId | None = None
   

    def __post_init__(self) -> None:
        if not isinstance(self.id, ActivityId):
            raise TypeError("Activity id must be an ActivityId.")

        if not isinstance(self.context_id, ContextId):
            raise TypeError(
                "Activity context_id must be a ContextId."
            )

        if (
            self.objective_id is not None
            and not isinstance(self.objective_id, ObjectiveId)
        ):
            raise TypeError(
                "Activity objective_id must be an ObjectiveId or None."
            )

        if not isinstance(self.status, ActivityStatus):
            raise TypeError(
                "Activity status must be an ActivityStatus."
            )

        if not isinstance(self.created_at, datetime):
            raise TypeError(
                "Activity created_at must be a datetime."
            )

        if not isinstance(self.updated_at, datetime):
            raise TypeError(
                "Activity updated_at must be a datetime."
            )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Activity):
            return NotImplemented

        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
