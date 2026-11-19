from novacore.kernel.identity import ActivityId, WorkId
from novacore.kernel.work import Work


#A. Work originating from Planning
work = Work(
    id=WorkId("work-001"),
    activity_id=ActivityId("activity-001"),
    planning_id=PlanningId("planning-001"),
    description="Research competitors in the target market.",
)

#B.  Work created directly
work = Work(
    id=WorkId("work-002"),
    activity_id=ActivityId("activity-001"),
    planning_id=None,
    description="Prepare an additional market research report.",
)