
from dataclasses import FrozenInstanceError

import pytest

from novacore.kernel.execution import Execution
from novacore.kernel.identity import (
    ExecutionId,
    AssignmentId,
    WorkId,
)


def create_execution(
    execution_id="execution-001",
    assignment_id="assignment-001",
):
    return Execution(
        id=ExecutionId(execution_id),
        assignment_id=AssignmentId(assignment_id),
    )


def test_execution_creation():
    execution = create_execution()

    assert execution.id == ExecutionId("execution-001")
    assert execution.assignment_id == AssignmentId("assignment-001")


def test_execution_requires_execution_id():
    with pytest.raises(TypeError):
        Execution(
            id=WorkId("work-001"),
            assignment_id=AssignmentId("assignment-001"),
        )


def test_execution_requires_assignment_id():
    with pytest.raises(TypeError):
        Execution(
            id=ExecutionId("execution-001"),
            assignment_id=WorkId("work-001"),
        )


def test_execution_is_immutable():
    execution = create_execution()

    with pytest.raises(FrozenInstanceError):
        execution.assignment_id = AssignmentId("assignment-002")


def test_execution_equality_uses_identity():
    first = create_execution(
        execution_id="execution-001",
        assignment_id="assignment-001",
    )

    second = create_execution(
        execution_id="execution-001",
        assignment_id="assignment-002",
    )

    assert first == second


def test_execution_with_different_ids_is_not_equal():
    first = create_execution(execution_id="execution-001")
    second = create_execution(execution_id="execution-002")

    assert first != second


def test_execution_hash_uses_identity():
    first = create_execution()
    second = create_execution()

    assert hash(first) == hash(second)


def test_execution_does_not_embed_assignment():
    execution = create_execution()

    assert isinstance(execution.assignment_id, AssignmentId)
    assert not hasattr(execution, "assignment")

