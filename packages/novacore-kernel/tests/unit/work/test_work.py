import pytest

from novacore.kernel.identity import ActivityId, PlanningId, WorkId
from novacore.kernel.work import Work


def make_work(**overrides):
    values = {
        "id": WorkId("work-1"),
        "activity_id": ActivityId("activity-1"),
        "description": "Prepare campaign research",
    }
    values.update(overrides)
    return Work(**values)


def test_work_creation_without_planning_reference():
    work = make_work()
    assert work.planning_id is None


def test_work_creation_with_optional_planning_reference():
    work = make_work(planning_id=PlanningId("planning-1"))
    assert work.planning_id == PlanningId("planning-1")


@pytest.mark.parametrize("value", ["", "   ", "\t"])
def test_work_rejects_empty_description(value):
    with pytest.raises(ValueError):
        make_work(description=value)


def test_work_rejects_wrong_types():
    with pytest.raises(TypeError):
        make_work(id="work-1")
    with pytest.raises(TypeError):
        make_work(activity_id="activity-1")
    with pytest.raises(TypeError):
        make_work(description=123)
    with pytest.raises(TypeError):
        make_work(planning_id="planning-1")


def test_work_is_immutable_and_identity_based():
    first = make_work()
    same_identity = make_work(description="A different description")
    assert first == same_identity
    assert hash(first) == hash(same_identity)
    with pytest.raises((AttributeError, TypeError)):
        first.description = "Changed"

