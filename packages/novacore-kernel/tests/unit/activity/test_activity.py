from datetime import datetime

import pytest

from novacore.kernel.activity import Activity, ActivityStatus
from novacore.kernel.identity import ActivityId, ContextId, ObjectiveId, RequestId


def make_activity(**overrides):
    values = {
        "id": ActivityId("activity-1"),
        "context_id": ContextId("context-1"),
        "status": ActivityStatus.DRAFT,
        "created_at": datetime(2026, 1, 1, 10, 0),
        "updated_at": datetime(2026, 1, 1, 10, 0),
    }
    values.update(overrides)
    return Activity(**values)


def test_activity_creation_with_optional_references():
    activity = make_activity(
        request_id=RequestId("request-1"),
        objective_id=ObjectiveId("objective-1"),
    )
    assert activity.request_id == RequestId("request-1")
    assert activity.objective_id == ObjectiveId("objective-1")


def test_activity_optional_references_default_to_none():
    activity = make_activity()
    assert activity.request_id is None
    assert activity.objective_id is None


def test_activity_identity_equality_and_hash():
    first = make_activity()
    second = make_activity(status=ActivityStatus.ACTIVE)
    assert first == second
    assert hash(first) == hash(second)


def test_activity_is_immutable():
    activity = make_activity()
    with pytest.raises((AttributeError, TypeError)):
        activity.status = ActivityStatus.ACTIVE


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("id", "activity-1"),
        ("context_id", "context-1"),
        ("status", "draft"),
        ("created_at", "2026-01-01"),
        ("updated_at", "2026-01-01"),
        ("request_id", "request-1"),
        ("objective_id", "objective-1"),
    ],
)
def test_activity_rejects_wrong_field_types(field, value):
    with pytest.raises(TypeError):
        make_activity(**{field: value})

