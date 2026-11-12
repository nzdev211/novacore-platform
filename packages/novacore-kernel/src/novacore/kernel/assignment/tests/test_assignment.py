x
from dataclasses import FrozenInstanceError

import pytest

from novacore.kernel.assignment import Assignment
from novacore.kernel.identity import (
    AssignmentId,
    WorkId,
    WorkerId,
    ExecutionId,
)


def create_assignment(
    assignment_id="assignment-001",
    work_id="work-001",
    worker_id="worker-001",
):
    return Assignment(
        id=AssignmentId(assignment_id),
        work_id=WorkId(work_id),
        worker_id=WorkerId(worker_id),
    )


def test_assignment_creation():
    assignment = create_assignment()

    assert assignment.id == AssignmentId("assignment-001")
    assert assignment.work_id == WorkId("work-001")
    assert assignment.worker_id == WorkerId("worker-001")


def test_assignment_requires_assignment_id():
    with pytest.raises(TypeError):
        Assignment(
            id=WorkId("work-001"),
            work_id=WorkId("work-001"),
            worker_id=WorkerId("worker-001"),
        )


def test_assignment_requires_work_id():
    with pytest.raises(TypeError):
        Assignment(
            id=AssignmentId("assignment-001"),
            work_id=AssignmentId("assignment-002"),
            worker_id=WorkerId("worker-001"),
        )


def test_assignment_requires_worker_id():
    with pytest.raises(TypeError):
        Assignment(
            id=AssignmentId("assignment-001"),
            work_id=WorkId("work-001"),
            worker_id=WorkId("work-002"),
        )


def test_assignment_is_immutable():
    assignment = create_assignment()

    with pytest.raises(FrozenInstanceError):
        assignment.worker_id = WorkerId("worker-002")


def test_assignment_equality_uses_identity():
    first = create_assignment(
        assignment_id="assignment-001",
        work_id="work-001",
        worker_id="worker-001",
    )

    second = create_assignment(
        assignment_id="assignment-001",
        work_id="work-002",
        worker_id="worker-002",
    )

    assert first == second


def test_assignment_with_different_ids_is_not_equal():
    first = create_assignment(assignment_id="assignment-001")
    second = create_assignment(assignment_id="assignment-002")

    assert first != second


def test_assignment_hash_uses_identity():
    first = create_assignment()
    second = create_assignment()

    assert hash(first) == hash(second)


def test_assignment_is_not_an_execution():
    assignment = create_assignment()

    assert not isinstance(assignment, ExecutionId)

