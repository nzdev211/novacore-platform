from datetime import datetime, timezone

from novacore.kernel.identity import ActivityId, ExecutionId, WorkId
from novacore.runtime.ports import ReviewRecord, ReviewStatus
from novacore.firestore.review_store import FirestoreReviewStore


class Snapshot:
    def __init__(self, exists, data=None):
        self.exists = exists
        self._data = data

    def to_dict(self):
        return self._data


class Document:
    def __init__(self, collection, doc_id):
        self.collection = collection
        self.doc_id = doc_id

    def get(self, transaction=None):
        return self.collection.docs.get(self.doc_id, Snapshot(False))

    def set(self, data):
        self.collection.docs[self.doc_id] = Snapshot(True, data)

    def create(self, data):
        if self.doc_id in self.collection.docs:
            raise RuntimeError("exists")
        self.collection.docs[self.doc_id] = Snapshot(True, data)


class Collection:
    def __init__(self):
        self.docs = {}

    def document(self, doc_id):
        return Document(self, doc_id)


class Client:
    def __init__(self):
        self.collections = {}

    def collection(self, name):
        return self.collections.setdefault(name, Collection())

    def transaction(self):
        class Transaction:
            def create(self, ref, data):
                ref.create(data)
            def set(self, ref, data):
                ref.set(data)
        return Transaction()


def record():
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return ReviewRecord(
        review_id="review 1",
        activity_id=ActivityId("activity-1"),
        work_id=WorkId("work-1"),
        execution_id=ExecutionId("execution-1"),
        status=ReviewStatus.PENDING,
        created_at=now,
        updated_at=now,
    )


def test_firestore_review_store_round_trip(monkeypatch):
    # Emulate the Firestore transactional decorator without requiring the SDK.
    import sys
    import types
    fake_firestore = types.SimpleNamespace(transactional=lambda fn: fn)
    fake_google_cloud = types.ModuleType("google.cloud")
    fake_google_cloud.firestore = fake_firestore
    monkeypatch.setitem(sys.modules, "google.cloud", fake_google_cloud)

    client = Client()
    store = FirestoreReviewStore(client)
    item = record()
    store.create_review(item)
    assert store.load_review(item.review_id) == item

