import pytest

from novacore.kernel.identity import CapabilityId, WorkerId
from novacore.kernel.worker import Worker


def test_worker_creation_without_capabilities():
    worker = Worker(WorkerId("worker-1"))
    assert worker.capability_ids == ()


def test_worker_references_multiple_capabilities():
    worker = Worker(
        WorkerId("worker-1"),
        (CapabilityId("research"), CapabilityId("writing")),
    )
    assert len(worker.capability_ids) == 2


def test_worker_rejects_non_tuple_capability_collection():
    with pytest.raises(TypeError):
        Worker(WorkerId("worker-1"), [CapabilityId("research")])


def test_worker_rejects_wrong_capability_reference_type():
    with pytest.raises(TypeError):
        Worker(WorkerId("worker-1"), ("research",))


def test_worker_rejects_duplicate_capabilities():
    capability_id = CapabilityId("research")
    with pytest.raises(ValueError):
        Worker(WorkerId("worker-1"), (capability_id, capability_id))


def test_worker_rejects_wrong_id_type():
    with pytest.raises(TypeError):
        Worker("worker-1")


def test_worker_is_immutable_and_identity_based():
    first = Worker(WorkerId("worker-1"), (CapabilityId("research"),))
    same_identity = Worker(WorkerId("worker-1"))
    assert first == same_identity
    assert hash(first) == hash(same_identity)
    with pytest.raises((AttributeError, TypeError)):
        first.capability_ids = ()

