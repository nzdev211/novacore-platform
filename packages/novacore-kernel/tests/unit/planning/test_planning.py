import pytest

from novacore.kernel.identity import ActivityId, ObjectiveId, PlanningId
from novacore.kernel.planning import Planning


def test_planning_creation_and_identity_equality():
    first = Planning(
        PlanningId("planning-1"),
        ActivityId("activity-1"),
        ObjectiveId("objective-1"),
        "Research audience",
    )
    same_identity = Planning(
        PlanningId("planning-1"),
        ActivityId("activity-2"),
        ObjectiveId("objective-2"),
        "Different plan",
    )
    assert first == same_identity
    assert hash(first) == hash(same_identity)


@pytest.mark.parametrize("value", ["", "   "])
def test_planning_rejects_empty_description(value):
    with pytest.raises(ValueError):
        Planning(
            PlanningId("planning-1"),
            ActivityId("activity-1"),
            ObjectiveId("objective-1"),
            value,
        )


def test_planning_rejects_wrong_types():
    with pytest.raises(TypeError):
        Planning("planning-1", ActivityId("activity-1"), ObjectiveId("objective-1"), "Plan")
    with pytest.raises(TypeError):
        Planning(PlanningId("planning-1"), "activity-1", ObjectiveId("objective-1"), "Plan")
    with pytest.raises(TypeError):
        Planning(PlanningId("planning-1"), ActivityId("activity-1"), "objective-1", "Plan")

