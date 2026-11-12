import pytest

from novacore.kernel.assignment import Assignment
from novacore.kernel.identity import AssignmentId, WorkId, WorkerId


def make_assignment(**overrides):
    values = {
        "id": AssignmentId("assignment-1"),
        "work_id": WorkId("work-1"),
        "worker_id": WorkerId("worker-1"),
    }
    values.update(overrides)
    return Assignment(**values)


def test_assignment_connects_work_and_worker():
    assignment = make_assignment()
    assert assignment.work_id == WorkId("work-1")
    assert assignment.worker_id == WorkerId("worker-1")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("id", "assignment-1"),
        ("work_id", "work-1"),
        ("worker_id", "worker-1"),
    ],
)
def test_assignment_rejects_wrong_reference_types(field, value):
    with pytest.raises(TypeError):
        make_assignment(**{field: value})


def test_assignment_is_immutable_and_identity_based():
    first = make_assignment()
    same_identity = make_assignment(
        work_id=WorkId("work-2"),
        worker_id=WorkerId("worker-2"),
    )
    assert first == same_identity
    assert hash(first) == hash(same_identity)
    with pytest.raises((AttributeError, TypeError)):
        first.worker_id = WorkerId("worker-3")

