from novacore.kernel.identity import ActivityId, WorkId
from novacore.kernel.work import Work

work = Work(
    id=WorkId("work-001"),
    activity_id=ActivityId("activity-001"),
    description="Research competitors in the target market.",
)
