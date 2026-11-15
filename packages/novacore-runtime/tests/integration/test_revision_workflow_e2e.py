from __future__ import annotations

from dataclasses import dataclass
from fastapi import FastAPI
from fastapi.testclient import TestClient

from novacore.fastapi.revisions import create_revision_service_router
from novacore.runtime.ports.revision_workflow import (
    RevisionInProgressError, RevisionResult, RevisionSource,
)
from novacore.runtime.services.revision_workflow import (
    RevisionNotAllowedError, RevisionWorkflowService,
)


@dataclass
class Source:
    review_id: str = "review-original"
    activity_id: str = "activity-1"
    work_id: str = "work-1"
    execution_id: str = "execution-1"
    review_status: str = "CHANGES_REQUESTED"
    review_feedback: str | None = "Make the camera movement slower."
    execution_input: dict = None
    execution_output: dict = None

    def __post_init__(self):
        self.execution_input = self.execution_input or {"brief": "A cinematic shot"}
        self.execution_output = self.execution_output or {"shot": "original"}

    def as_revision_source(self):
        return RevisionSource(
            review_id=self.review_id, activity_id=self.activity_id,
            work_id=self.work_id, execution_id=self.execution_id,
            review_status=self.review_status, review_feedback=self.review_feedback,
            execution_input=self.execution_input, execution_output=self.execution_output,
        )


class InMemorySourceStore:
    def __init__(self, source: Source):
        self.source = source
        self.calls = []

    def load_revision_source(self, *, review_id: str, creator_id: str):
        self.calls.append((review_id, creator_id))
        if review_id != self.source.review_id:
            return None
        return self.source.as_revision_source()


class InMemoryRevisionRecordStore:
    def __init__(self):
        self.records = {}

    def reserve_revision(self, *, source_review_id: str, idempotency_key: str):
        key = (source_review_id, idempotency_key)
        current = self.records.get(key)
        if current is None:
            self.records[key] = {"state": "reserved"}
            return None
        if current["state"] == "completed":
            return current["result"]
        raise RevisionInProgressError("Revision is already reserved.")

    def complete_revision(self, *, source_review_id: str, idempotency_key: str, result: RevisionResult):
        key = (source_review_id, idempotency_key)
        assert self.records[key]["state"] == "reserved"
        self.records[key] = {"state": "completed", "result": result}

    def release_revision(self, *, source_review_id: str, idempotency_key: str):
        key = (source_review_id, idempotency_key)
        if self.records.get(key, {}).get("state") == "reserved":
            del self.records[key]


class FakeExistingRuntimeExecutionPath:
    """Test double for the normal Runtime lifecycle; never calls a provider."""

    def __init__(self):
        self.calls = []
        self.fail = False

    def __call__(self, source, additional_instructions, idempotency_key):
        self.calls.append((source, additional_instructions, idempotency_key))
        if self.fail:
            raise RuntimeError("simulated execution interruption")
        return (
            "execution-2", "SUCCEEDED",
            {"shot": "revised", "instructions": additional_instructions},
        )


class InMemoryReviewCreator:
    def __init__(self):
        self.records = {}

    def create_pending_review(
        self, *, activity_id, work_id, execution_id, source_review_id, creator_id
    ):
        review_id = f"review-generated-{len(self.records) + 1}"
        self.records[review_id] = {
            "activity_id": activity_id, "work_id": work_id,
            "execution_id": execution_id, "status": "PENDING",
            "source_review_id": source_review_id, "creator_id": creator_id,
        }
        return review_id


def build_client(source=None, *, authenticated_creator="creator-1", fail_execution=False):
    source = source or Source()
    source_store = InMemorySourceStore(source)
    record_store = InMemoryRevisionRecordStore()
    execution_path = FakeExistingRuntimeExecutionPath()
    execution_path.fail = fail_execution
    reviews = InMemoryReviewCreator()

    from novacore.runtime.ports.revision_execution import CallbackRevisionExecutionPort
    service = RevisionWorkflowService(
        source_store=source_store,
        execution_port=CallbackRevisionExecutionPort(execution_path),
        revision_store=record_store,
        review_creator=reviews,
    )
    app = FastAPI()
    app.include_router(create_revision_service_router(
        revision_service=service,
        authenticate_creator=lambda: authenticated_creator,
    ))
    return TestClient(app), source_store, record_store, execution_path, reviews


def test_end_to_end_revision_and_idempotent_replay():
    client, sources, reservations, execution, reviews = build_client()
    payload = {
        "additional_instructions": "Slow the camera movement.",
        "idempotency_key": "revision-key-001",
    }

    first = client.post("/reviews/review-original/revisions", json=payload)
    second = client.post("/reviews/review-original/revisions", json=payload)

    assert first.status_code == 202
    assert first.json()["execution_id"] == "execution-2"
    assert first.json()["review_id"] == "review-generated-1"
    assert first.json()["status"] == "PENDING"
    assert first.json()["replayed"] is False
    assert second.status_code == 202
    assert second.json()["replayed"] is True
    assert second.json()["review_id"] == first.json()["review_id"]
    assert len(execution.calls) == 1
    assert len(reviews.records) == 1
    assert sources.calls == [("review-original", "creator-1")]
    assert reservations.records[("review-original", "revision-key-001")]["state"] == "completed"


def test_end_to_end_rejects_review_not_marked_changes_requested():
    client, _, reservations, execution, reviews = build_client(Source(review_status="APPROVED"))
    response = client.post(
        "/reviews/review-original/revisions", json={"idempotency_key": "key-approved"}
    )
    assert response.status_code == 409
    assert execution.calls == []
    assert reviews.records == {}
    assert ("review-original", "key-approved") not in reservations.records


def test_end_to_end_missing_review_returns_404_and_releases_reservation():
    client, _, reservations, execution, _ = build_client()
    response = client.post(
        "/reviews/missing-review/revisions", json={"idempotency_key": "key-missing"}
    )
    assert response.status_code == 404
    assert execution.calls == []
    assert ("missing-review", "key-missing") not in reservations.records


def test_end_to_end_execution_failure_keeps_reservation_for_reconciliation():
    client, _, reservations, execution, reviews = build_client(fail_execution=True)
    payload = {"idempotency_key": "key-uncertain"}
    first = client.post("/reviews/review-original/revisions", json=payload)
    second = client.post("/reviews/review-original/revisions", json=payload)

    assert first.status_code == 503
    assert second.status_code == 409
    assert len(execution.calls) == 1
    assert reviews.records == {}
    assert reservations.records[("review-original", "key-uncertain")]["state"] == "reserved"


def test_end_to_end_authenticated_identity_is_not_accepted_from_payload():
    client, sources, _, execution, _ = build_client(authenticated_creator="verified-user")
    response = client.post(
        "/reviews/review-original/revisions",
        json={"idempotency_key": "key-auth", "creator_id": "forged-user"},
    )
    assert response.status_code == 422
    assert sources.calls == []
    assert execution.calls == []

