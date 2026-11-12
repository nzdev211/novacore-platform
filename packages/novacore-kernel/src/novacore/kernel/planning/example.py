from novacore.kernel.identity import (
    ActivityId,
    ObjectiveId,
    PlanningId,
)
from novacore.kernel.planning import Planning

planning = Planning(
    id=PlanningId("planning-001"),
    activity_id=ActivityId("activity-001"),
    objective_id=ObjectiveId("objective-001"),
    description=(
        "Research the target audience, develop campaign concepts, "
        "and prepare marketing content."
    ),
)
