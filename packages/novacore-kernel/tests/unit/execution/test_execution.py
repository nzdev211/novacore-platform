import pytest

from novacore.kernel.execution import Execution
from novacore.kernel.identity import AssignmentId, ExecutionId


def make_execution(**overrides):
    values = {
        "id": ExecutionId("execution-1"),
        "assignment_id": AssignmentId("assignment-1"),
    }
    values.update(overrides)
    return Execution(**values)


def test_execution_creation():
    execution = make_execution()
    assert execution.id == ExecutionId("execution-1")
    assert execution.assignment_id == AssignmentId("assignment-1")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("id", "execution-1"),
        ("assignment_id", "assignment-1"),
    ],
)
def test_execution_rejects_wrong_reference_types(field, value):
    with pytest.raises(TypeError):
        make_execution(**{field: value})


def test_execution_is_immutable_and_identity_based():
    first = make_execution()
    same_identity = make_execution(assignment_id=AssignmentId("assignment-2"))
    assert first == same_identity
    assert hash(first) == hash(same_identity)
    with pytest.raises((AttributeError, TypeError)):
        first.assignment_id = AssignmentId("assignment-3")


def test_multiple_executions_can_reference_the_same_assignment():
    assignment_id = AssignmentId("assignment-1")
    first = Execution(ExecutionId("execution-1"), assignment_id)
    second = Execution(ExecutionId("execution-2"), assignment_id)
    assert first.assignment_id == second.assignment_id
    assert first.id != second.id

