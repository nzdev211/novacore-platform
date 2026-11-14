from fastapi import FastAPI
from fastapi.testclient import TestClient

from novacore.fastapi.revision_history import create_revision_history_router


def make_client(callback):
    app = FastAPI()
    app.include_router(create_revision_history_router(
        load_revision_history=callback,
        authenticate_reviewer=lambda: "reviewer-1",
    ))
    return TestClient(app)


def sample_history():
    return {
        "activity_id": "activity-1",
        "work_id": "work-1",
        "entries": [
            {
                "review_id": "review-1", "execution_id": "execution-1",
                "activity_id": "activity-1", "work_id": "work-1",
                "review_status": "CHANGES_REQUESTED", "execution_status": "SUCCEEDED",
                "created_at": "2026-11-14T10:00:00Z", "feedback": "Change the camera angle",
            },
            {
                "review_id": "review-2", "execution_id": "execution-2",
                "activity_id": "activity-1", "work_id": "work-1",
                "review_status": "PENDING", "execution_status": "SUCCEEDED",
                "created_at": "2026-11-14T11:00:00Z", "source_review_id": "review-1",
            },
        ],
    }


def test_returns_history_for_authenticated_reviewer():
    calls = []

    def load_revision_history(**kwargs):
        calls.append(kwargs)
        return sample_history()

    response = make_client(load_revision_history).get("/reviews/review-2/history")
    assert response.status_code == 200
    assert [entry["execution_id"] for entry in response.json()["entries"]] == ["execution-1", "execution-2"]
    assert calls == [{"review_id": "review-2", "reviewer_id": "reviewer-1"}]


def test_returns_404_for_missing_history():
    response = make_client(lambda **kwargs: None).get("/reviews/missing/history")
    assert response.status_code == 404


def test_denies_unauthorized_history_access():
    def callback(**kwargs):
        raise PermissionError()

    response = make_client(callback).get("/reviews/review-2/history")
    assert response.status_code == 403


def test_rejects_history_that_does_not_include_requested_review():
    data = sample_history()
    data["entries"] = data["entries"][:1]
    response = make_client(lambda **kwargs: data).get("/reviews/not-in-chain/history")
    assert response.status_code == 409


def test_rejects_history_crossing_activity_or_work_boundaries():
    data = sample_history()
    data["entries"][1]["activity_id"] = "another-activity"
    response = make_client(lambda **kwargs: data).get("/reviews/review-2/history")
    assert response.status_code == 409

