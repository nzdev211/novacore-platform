from __future__ import annotations

import sys
import types

import pytest

from novacore.firestore.revision_store import (
    FirestoreRevisionRecordStore,
    RevisionReservationConflict,
)
from novacore.runtime.ports import PersistenceError, RevisionInProgressError, RevisionResult


class Snapshot:
    def __init__(self, data):
        self._data = data
        self.exists = data is not None

    def to_dict(self):
        return dict(self._data) if self._data is not None else None


class Document:
    def __init__(self, collection, doc_id):
        self.collection = collection
        self.id = doc_id

    def get(self, transaction=None):
        return Snapshot(self.collection.rows.get(self.id))


class Collection:
    def __init__(self):
        self.rows = {}

    def document(self, doc_id):
        return Document(self, doc_id)


class Transaction:
    def create(self, ref, data):
        if ref.id in ref.collection.rows:
            raise RuntimeError("already exists")
        ref.collection.rows[ref.id] = dict(data)

    def set(self, ref, data):
        ref.collection.rows[ref.id] = dict(data)

    def delete(self, ref):
        ref.collection.rows.pop(ref.id, None)


class Client:
    def __init__(self):
        self.collections = {}

    def collection(self, name):
        return self.collections.setdefault(name, Collection())

    def transaction(self):
        return Transaction()


@pytest.fixture(autouse=True)
def fake_firestore_sdk(monkeypatch):
    firestore = types.ModuleType("google.cloud.firestore")
    firestore.transactional = lambda fn: fn
    google = types.ModuleType("google")
    cloud = types.ModuleType("google.cloud")
    cloud.firestore = firestore
    google.cloud = cloud
    monkeypatch.setitem(sys.modules, "google", google)
    monkeypatch.setitem(sys.modules, "google.cloud", cloud)
    monkeypatch.setitem(sys.modules, "google.cloud.firestore", firestore)


def make_store():
    client = Client()
    return FirestoreRevisionRecordStore(client), client


def test_reserve_creates_one_attempt_and_blocks_duplicate_in_progress_key():
    assert issubclass(RevisionReservationConflict, RevisionInProgressError)
    store, client = make_store()
    assert store.reserve_revision(source_review_id="review-1", idempotency_key="key-1") is None
    with pytest.raises(RevisionReservationConflict):
        store.reserve_revision(source_review_id="review-1", idempotency_key="key-1")
    assert len(client.collection("revision_attempts").rows) == 1


def test_completed_revision_is_returned_for_safe_replay():
    store, _ = make_store()
    store.reserve_revision(source_review_id="review-1", idempotency_key="key-1")
    result = RevisionResult(
        source_review_id="review-1", activity_id="activity-1", work_id="work-1",
        execution_id="execution-2", review_id="review-2",
    )
    store.complete_revision(
        source_review_id="review-1", idempotency_key="key-1", result=result
    )
    replay = store.reserve_revision(source_review_id="review-1", idempotency_key="key-1")
    assert replay == result


def test_release_only_removes_unfinished_reservation():
    store, client = make_store()
    store.reserve_revision(source_review_id="review-1", idempotency_key="key-1")
    store.release_revision(source_review_id="review-1", idempotency_key="key-1")
    assert client.collection("revision_attempts").rows == {}

    store.reserve_revision(source_review_id="review-1", idempotency_key="key-2")
    result = RevisionResult(
        source_review_id="review-1", activity_id="activity-1", work_id="work-1",
        execution_id="execution-2", review_id="review-2",
    )
    store.complete_revision(
        source_review_id="review-1", idempotency_key="key-2", result=result
    )
    store.release_revision(source_review_id="review-1", idempotency_key="key-2")
    assert len(client.collection("revision_attempts").rows) == 1


def test_completion_requires_existing_reservation():
    store, _ = make_store()
    result = RevisionResult(
        source_review_id="review-1", activity_id="activity-1", work_id="work-1",
        execution_id="execution-2", review_id="review-2",
    )
    with pytest.raises(RevisionReservationConflict):
        store.complete_revision(
            source_review_id="review-1", idempotency_key="key-1", result=result
        )


def test_reservation_is_scoped_to_source_review_and_key():
    store, client = make_store()
    store.reserve_revision(source_review_id="review-1", idempotency_key="same-key")
    store.reserve_revision(source_review_id="review-2", idempotency_key="same-key")
    assert len(client.collection("revision_attempts").rows) == 2


def test_invalid_key_is_rejected():
    store, _ = make_store()
    with pytest.raises(ValueError):
        store.reserve_revision(source_review_id="review-1", idempotency_key=" ")

