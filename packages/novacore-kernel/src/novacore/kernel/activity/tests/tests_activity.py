
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from novacore.kernel.activity import Activity, ActivityStatus
from novacore.kernel.identity import (
    ActivityId,
    ContextId,
    ObjectiveId,
    WorkId,
)


def create_activity(
    activity_id="activity-001",
    context_id="context-001",
    objective_id=None,
    status=ActivityStatus.DRAFT,
):
    now = datetime.now(timezone.utc)

    return Activity(
        id=ActivityId(activity_id),
        context_id=ContextId(context_id),
        objective_id=(
            ObjectiveId(objective_id)
            if objective_id is not None
            else None
        ),
        status=status,
        created_at=now,
        updated_at=now,
    )


def test_activity_creation():
    activity = create_activity(
        objective_id="objective-001",
    )

    assert activity.id == ActivityId("activity-001")
    assert activity.context_id == ContextId("context-001")
    assert activity.objective_id == ObjectiveId("objective-001")
    assert activity.status == ActivityStatus.DRAFT


def test_activity_can_exist_without_objective():
    activity = create_activity()

    assert activity.objective_id is None


def test_activity_requires_activity_id():
    with pytest.raises(TypeError):
        Activity(
            id=WorkId("work-001"),
            context_id=ContextId("context-001"),
            objective_id=None,
            status=ActivityStatus.DRAFT,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )


def test_activity_requires_context_id():
    with pytest.raises(TypeError):
        Activity(
            id=ActivityId("activity-001"),
            context_id=WorkId("work-001"),
            objective_id=None,
            status=ActivityStatus.DRAFT,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )


def test_activity_requires_valid_objective_id():
    with pytest.raises(TypeError):
        Activity(
            id=ActivityId("activity-001"),
            context_id=ContextId("context-001"),
            objective_id=WorkId("work-001"),
            status=ActivityStatus.DRAFT,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )


def test_activity_requires_activity_status():
    with pytest.raises(TypeError):
        create_activity(status="draft")


def test_activity_requires_datetime_values():
    with pytest.raises(TypeError):
        Activity(
            id=ActivityId("activity-001"),
            context_id=ContextId("context-001"),
            objective_id=None,
            status=ActivityStatus.DRAFT,
            created_at="2026-11-11",
            updated_at=datetime.now(timezone.utc),
        )


def test_activity_is_immutable():
    activity = create_activity()

    with pytest.raises(FrozenInstanceError):
        activity.status = ActivityStatus.ACTIVE


def test_activity_equality_uses_identity():
    first = create_activity(
        activity_id="activity-001",
        status=ActivityStatus.DRAFT,
    )

    second = create_activity(
        activity_id="activity-001",
        status=ActivityStatus.ACTIVE,
    )

    assert first == second


def test_activity_different_ids_are_not_equal():
    first = create_activity(activity_id="activity-001")
    second = create_activity(activity_id="activity-002")

    assert first != second


def test_activity_hash_uses_identity():
    first = create_activity(activity_id="activity-001")
    second = create_activity(activity_id="activity-001")

    assert hash(first) == hash(second)


def test_activity_does_not_embed_work():
    activity = create_activity()

    assert not hasattr(activity, "work")
    assert not hasattr(activity, "works")

