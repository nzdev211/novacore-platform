from fastapi import FastAPI
from fastapi.testclient import TestClient

from novacore.fastapi.revisions import create_revision_router


def make_client(callback):
    app = FastAPI()
    app.include_router(create_revision_router(
        create_revision=callback,
        authenticate_creator=lambda: "creator-1",
    ))
    return TestClient(app)


def test_starts_revision_using_authenticated_creator_and_returns_new_review():
    calls = []

    def create_revision(**kwargs):
        calls.append(kwargs)
        return {
            "source_review_id": "review-1",
            "activity_id": "activity-1",
            "work_id": "work-1",
            "execution_id": "execution-2",
            "review_id": "review-2",
            "status": "PENDING",
        }

    response = make_client(create_revision).post(
        "/reviews/review-1/revisions",
        json={"additional_instructions": "Use a lower camera angle", "idempotency_key": "rev-1"},
    )

    assert response.status_code == 202
    assert response.json()["review_id"] == "review-2"
    assert calls == [{
        "source_review_id": "review-1",
        "creator_id": "creator-1",
        "additional_instructions": "Use a lower camera angle",
        "idempotency_key": "rev-1",
    }]


def test_rejects_payload_creator_identity_and_unknown_fields():
    client = make_client(lambda **kwargs: None)
    response = client.post(
        "/reviews/review-1/revisions",
        json={"idempotency_key": "rev-1", "creator_id": "forged"},
    )
    assert response.status_code == 422


def test_maps_permission_error_to_forbidden():
    def create_revision(**kwargs):
        raise PermissionError()

    response = make_client(create_revision).post(
        "/reviews/review-1/revisions", json={"idempotency_key": "rev-1"}
    )
    assert response.status_code == 403


def test_rejects_result_for_different_source_review():
    def create_revision(**kwargs):
        return {
            "source_review_id": "other-review", "activity_id": "a", "work_id": "w",
            "execution_id": "e2", "review_id": "r2", "status": "PENDING",
        }

    response = make_client(create_revision).post(
        "/reviews/review-1/revisions", json={"idempotency_key": "rev-1"}
    )
    assert response.status_code == 409

