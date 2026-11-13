]from datetime import datetime, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from novacore.kernel.identity import ActivityId, ExecutionId, WorkId
from novacore.runtime.ports import ReviewRecord, ReviewStatus
from novacore.runtime.services.human_review import HumanReviewService
from novacore.fastapi.reviews import create_human_review_router


class MemoryReviewStore:
    def __init__(self):
        self.records = {}

    def create_review(self, record):
        if record.review_id in self.records:
            raise ValueError("duplicate review ID")
        self.records[record.review_id] = record

    def load_review(self, review_id):
        return self.records.get(review_id)

    def transition_review(self, record, *, expected_status):
        current = self.records[record.review_id]
        if current.status is not expected_status:
            raise RuntimeError("status conflict")
        self.records[record.review_id] = record


@pytest.fixture
def client():
    store = MemoryReviewStore()
    service = HumanReviewService(store)

    def authenticated_reviewer():
        return "authenticated-user-42"

    app = FastAPI()
    app.include_router(
        create_human_review_router(
            review_service=service,
            review_store=store,
            authenticate_reviewer=authenticated_reviewer,
        )
    )
    return TestClient(app)


def test_submit_review_requires_authenticated_dependency_and_returns_pending(client):
    response = client.post(
        "/reviews",
        json={
            "review_id": "r-1",
            "activity_id": "a-1",
            "work_id": "w-1",
            "execution_id": "e-1",
        },
    )
    assert response.status_code == 201
    assert response.json()["status"] == "pending"
    assert response.json()["reviewer_id"] is None


def test_get_review_returns_404_when_missing(client):
    response = client.get("/reviews/missing")
    assert response.status_code == 404


def test_decision_uses_authenticated_identity_not_request_body(client):
    client.post(
        "/reviews",
        json={
            "review_id": "r-2",
            "activity_id": "a-1",
            "work_id": "w-1",
            "execution_id": "e-1",
        },
    )
    response = client.post(
        "/reviews/r-2/decision",
        json={"decision": "approved", "feedback": "Looks good."},
    )
    assert response.status_code == 200
    assert response.json()["reviewer_id"] == "authenticated-user-42"
    assert response.json()["status"] == "approved"


def test_decision_cannot_be_submitted_twice(client):
    client.post(
        "/reviews",
        json={
            "review_id": "r-3",
            "activity_id": "a-1",
            "work_id": "w-1",
            "execution_id": "e-1",
        },
    )
    payload = {"decision": "rejected", "feedback": "Needs work."}
    assert client.post("/reviews/r-3/decision", json=payload).status_code == 200
    assert client.post("/reviews/r-3/decision", json=payload).status_code == 409

