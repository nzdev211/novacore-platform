import sys
import types
from datetime import datetime, timezone

import pytest

from novacore.kernel.activity import Activity, ActivityStatus
from novacore.kernel.assignment import Assignment
from novacore.kernel.context import Context, ContextAttributes
from novacore.kernel.contract import Contract
from novacore.kernel.execution import Execution
from novacore.kernel.identity import (
    ActivityId, AssignmentId, ContextId, ContractId, ExecutionId,
    ObjectiveId, PlanningId, RequestId, WorkId, WorkerId,
)
from novacore.kernel.objective import Objective
from novacore.kernel.planning import Planning
from novacore.kernel.request import Request
from novacore.kernel.work import Work
from novacore.firestore.workflow_store import FirestoreWorkflowStore, _document_id


class FakeDocument:
    def __init__(self, collection, document_id):
        self.collection = collection
        self.collection_name = collection.name
        self.document_id = document_id
        self.payload = None

    def set(self, payload):
        self.payload = payload
        self.collection.documents[self.document_id] = payload

    def get(self):
        return FakeSnapshot(self.collection.documents.get(self.document_id))


class FakeSnapshot:
    def __init__(self, payload):
        self.payload = payload
        self.exists = payload is not None

    def to_dict(self):
        return self.payload


class FakeCollection:
    def __init__(self, name):
        self.name = name
        self.documents = {}

    def document(self, document_id):
        return FakeDocument(self, document_id)

    def where(self, field, operator, value):
        assert operator == "=="
        return FakeQuery(self, field, value)


class FakeQuery:
    def __init__(self, collection, field, value):
        self.collection, self.field, self.value = collection, field, value

    def stream(self):
        return [FakeSnapshot(data) for data in self.collection.documents.values()
                if data.get(self.field) == self.value]


class FakeTransaction:
    def __init__(self):
        self.writes = []

    def set(self, ref, payload):
        self.writes.append((ref.collection_name, ref.document_id, payload))
        ref.collection.documents[ref.document_id] = payload

    def get(self, ref):
        return [FakeSnapshot(ref.collection.documents.get(ref.document_id))]


class FakeClient:
    def __init__(self):
        self.collections = {}
        self.tx = FakeTransaction()

    def collection(self, name):
        return self.collections.setdefault(name, FakeCollection(name))

    def transaction(self):
        return self.tx


@pytest.fixture
def fake_firestore(monkeypatch):
    module = types.ModuleType("google.cloud.firestore")

    def transactional(fn):
        def wrapped(transaction, *args, **kwargs):
            result = fn(transaction, *args, **kwargs)
            transaction.committed = True
            return result
        return wrapped

    module.transactional = transactional
    cloud = sys.modules.get("google.cloud")
    if cloud is None:
        cloud = types.ModuleType("google.cloud")
        monkeypatch.setitem(sys.modules, "google.cloud", cloud)
    monkeypatch.setattr(cloud, "firestore", module, raising=False)
    monkeypatch.setitem(sys.modules, "google.cloud.firestore", module)
    return module


@pytest.fixture
def records():
    now = datetime(2026, 11, 12, tzinfo=timezone.utc)
    request = Request(RequestId("request/1"), "Create storyboard shot")
    context = Context(ContextId("context/1"), ContextAttributes({
        "scene": "Bern 1905", "tags": ["historical", "comedy"],
        "nested": {"enabled": True},
    }))
    objective = Objective(ObjectiveId("objective/1"), "Create one shot")
    activity = Activity(
        id=ActivityId("activity/1"), context_id=context.id,
        status=ActivityStatus.ACTIVE, created_at=now, updated_at=now,
        request_id=request.id, objective_id=objective.id,
    )
    planning = Planning(
        PlanningId("planning/1"), activity.id, objective.id, "Plan shot"
    )
    work = Work(WorkId("work/1"), activity.id, "Generate shot", planning.id)
    contracts = (
        Contract(ContractId("contract/1"), work.id, "Keep Nana consistent"),
        Contract(ContractId("contract/2"), work.id, "Vertical 9:16"),
    )
    assignment = Assignment(
        AssignmentId("assignment/1"), work.id, WorkerId("worker/1")
    )
    execution = Execution(ExecutionId("execution/1"), assignment.id)
    return locals()


def test_initial_workflow_is_one_transaction(fake_firestore, records):
    client = FakeClient()
    store = FirestoreWorkflowStore(client=client)
    r = records

    store.save_initial_workflow(
        request=r["request"], context=r["context"], objective=r["objective"],
        activity=r["activity"], planning=r["planning"], work=r["work"],
        contracts=r["contracts"], assignment=r["assignment"],
    )

    writes = client.tx.writes
    assert client.tx.committed is True
    assert len(writes) == 9
    assert {item[0] for item in writes} == {
        "requests", "contexts", "objectives", "activities",
        "plannings", "works", "contracts", "assignments",
    }
    context_payload = next(payload for collection, _, payload in writes if collection == "contexts")
    assert context_payload["attributes"]["scene"] == "Bern 1905"
    assert context_payload["attributes"]["tags"] == ["historical", "comedy"]
    activity_payload = next(payload for collection, _, payload in writes if collection == "activities")
    assert activity_payload["status"] == "active"


def test_document_ids_safely_encode_slashes_and_unicode():
    encoded = _document_id(ActivityId("activity/日本"))
    assert "/" not in encoded
    assert encoded
    assert _document_id(ActivityId("same")) == _document_id(ActivityId("same"))
    long_id = _document_id(ActivityId("x" * 5000))
    assert len(long_id.encode("utf-8")) <= 1500
    assert long_id.startswith("sha256-")


def test_execution_is_saved_separately(fake_firestore, records):
    client = FakeClient()
    store = FirestoreWorkflowStore(client=client)
    store.save_execution(records["execution"])

    payload = client.collections["executions"].documents[
        _document_id(records["execution"].id)
    ]
    assert payload == {
        "id": "execution/1",
        "assignment_id": "assignment/1",
    }


def test_transaction_failure_is_wrapped(fake_firestore, records):
    class BrokenTransaction(FakeTransaction):
        def set(self, ref, payload):
            raise RuntimeError("write failed")

    client = FakeClient()
    client.tx = BrokenTransaction()
    store = FirestoreWorkflowStore(client=client)
    r = records

    from novacore.runtime.ports import PersistenceError
    with pytest.raises(PersistenceError, match="initial workflow"):
        store.save_initial_workflow(
            request=r["request"], context=r["context"], objective=r["objective"],
            activity=r["activity"], planning=r["planning"], work=r["work"],
            contracts=r["contracts"], assignment=r["assignment"],
        )


def test_load_workflow_rehydrates_all_related_records(records):
    client = FakeClient()
    store = FirestoreWorkflowStore(client=client)
    r = records
    payloads = [
        ("requests", r["request"].id, {"id": r["request"].id.value, "description": r["request"].description}),
        ("contexts", r["context"].id, {"id": r["context"].id.value, "attributes": {"scene": "Bern 1905", "tags": ["historical", "comedy"], "nested": {"enabled": True}}}),
        ("objectives", r["objective"].id, {"id": r["objective"].id.value, "description": r["objective"].description}),
        ("activities", r["activity"].id, {"id": r["activity"].id.value, "context_id": r["context"].id.value, "status": "active", "created_at": r["activity"].created_at, "updated_at": r["activity"].updated_at, "request_id": r["request"].id.value, "objective_id": r["objective"].id.value}),
        ("plannings", r["planning"].id, {"id": r["planning"].id.value, "activity_id": r["activity"].id.value, "objective_id": r["objective"].id.value, "description": r["planning"].description}),
        ("works", r["work"].id, {"id": r["work"].id.value, "activity_id": r["activity"].id.value, "planning_id": r["planning"].id.value, "description": r["work"].description}),
        ("assignments", r["assignment"].id, {"id": r["assignment"].id.value, "work_id": r["work"].id.value, "worker_id": r["assignment"].worker_id.value}),
        ("executions", r["execution"].id, {"id": r["execution"].id.value, "assignment_id": r["assignment"].id.value}),
    ]
    for collection, identifier, payload in payloads:
        store._ref(collection, identifier).set(payload)
    for contract in r["contracts"]:
        store._ref("contracts", contract.id).set({"id": contract.id.value, "work_id": contract.work_id.value, "description": contract.description})

    snapshot = store.load_workflow(r["activity"].id)

    assert snapshot is not None
    assert snapshot.activity == r["activity"]
    assert snapshot.context.attributes.values["scene"] == "Bern 1905"
    assert len(snapshot.planning) == 1
    assert len(snapshot.works) == 1
    assert len(snapshot.contracts) == 2
    assert snapshot.assignments == (r["assignment"],)
    assert snapshot.executions == (r["execution"],)


def test_load_workflow_returns_none_when_activity_is_missing():
    store = FirestoreWorkflowStore(client=FakeClient())
    assert store.load_workflow(ActivityId("missing")) is None


def test_execution_lifecycle_uses_compare_and_set(fake_firestore, records):
    from novacore.runtime.ports import ExecutionRecord, ExecutionStatus, PersistenceError

    client = FakeClient()
    store = FirestoreWorkflowStore(client=client)
    r = records
    pending = ExecutionRecord(
        r["execution"].id, r["assignment"].id, ExecutionStatus.PENDING,
        datetime(2026, 11, 12, tzinfo=timezone.utc),
    )
    store.transition_execution(pending, expected_status=None)
    running = ExecutionRecord(
        r["execution"].id, r["assignment"].id, ExecutionStatus.RUNNING,
        datetime(2026, 11, 12, tzinfo=timezone.utc),
    )
    store.transition_execution(running, expected_status=ExecutionStatus.PENDING)
    assert store.load_execution(r["execution"].id).status is ExecutionStatus.RUNNING
    with pytest.raises(PersistenceError, match="state conflict"):
        store.transition_execution(running, expected_status=ExecutionStatus.PENDING)


def test_idempotency_key_is_reserved_once_across_execution_ids(fake_firestore, records):
    from novacore.runtime.ports import ExecutionRecord, ExecutionStatus, PersistenceError
    client = FakeClient()
    store = FirestoreWorkflowStore(client=client)
    r = records
    now = datetime(2026, 11, 12, tzinfo=timezone.utc)
    first = ExecutionRecord(
        r["execution"].id, r["assignment"].id, ExecutionStatus.PENDING, now,
        idempotency_key="storyboard-shot-01-v1",
    )
    store.transition_execution(first, expected_status=None)
    running = ExecutionRecord(
        r["execution"].id, r["assignment"].id, ExecutionStatus.RUNNING, now,
        idempotency_key="storyboard-shot-01-v1",
    )
    store.transition_execution(running, expected_status=ExecutionStatus.PENDING)

    second_id = ExecutionId("execution/duplicate")
    second = ExecutionRecord(
        second_id, r["assignment"].id, ExecutionStatus.PENDING, now,
        idempotency_key="storyboard-shot-01-v1",
    )
    store.transition_execution(second, expected_status=None)
    duplicate_running = ExecutionRecord(
        second_id, r["assignment"].id, ExecutionStatus.RUNNING, now,
        idempotency_key="storyboard-shot-01-v1",
    )
    with pytest.raises(PersistenceError, match="already been reserved"):
        store.transition_execution(duplicate_running, expected_status=ExecutionStatus.PENDING)

