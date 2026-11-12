
from dataclasses import FrozenInstanceError

import pytest

from novacore.kernel.worker import Worker
from novacore.kernel.identity import (
    WorkerId,
    CapabilityId,
    WorkId,
)


def test_worker_creation():
    worker = Worker(
        id=WorkerId("worker-001"),
        capability_ids=(
            CapabilityId("capability-001"),
            CapabilityId("capability-002"),
        ),
    )

    assert worker.id == WorkerId("worker-001")
    assert len(worker.capability_ids) == 2


def test_worker_can_have_no_capabilities():
    worker = Worker(id=WorkerId("worker-001"))

    assert worker.capability_ids == ()


def test_worker_requires_worker_id():
    with pytest.raises(TypeError):
        Worker(id=WorkId("work-001"))


def test_worker_requires_tuple_for_capabilities():
    with pytest.raises(TypeError):
        Worker(
            id=WorkerId("worker-001"),
            capability_ids=[CapabilityId("capability-001")],
        )


def test_worker_rejects_invalid_capability_reference():
    with pytest.raises(TypeError):
        Worker(
            id=WorkerId("worker-001"),
            capability_ids=(WorkId("work-001"),),
        )


def test_worker_rejects_duplicate_capabilities():
    capability_id = CapabilityId("capability-001")

    with pytest.raises(ValueError):
        Worker(
            id=WorkerId("worker-001"),
            capability_ids=(capability_id, capability_id),
        )


def test_worker_is_immutable():
    worker = Worker(id=WorkerId("worker-001"))

    with pytest.raises(FrozenInstanceError):
        worker.id = WorkerId("worker-002")


def test_worker_equality_uses_identity():
    first = Worker(id=WorkerId("worker-001"))
    second = Worker(
        id=WorkerId("worker-001"),
        capability_ids=(CapabilityId("capability-001"),),
    )

    assert first == second


def test_worker_hash_uses_identity():
    first = Worker(id=WorkerId("worker-001"))
    second = Worker(id=WorkerId("worker-001"))

    assert hash(first) == hash(second)

