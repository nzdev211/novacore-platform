from fastapi import FastAPI
from fastapi.testclient import TestClient

from novacore.fastapi.review_context import create_review_context_router


def test_review_context_is_scoped_to_authenticated_reviewer():
    calls = []

    def load_review_context(*, review_id, reviewer_id):
        calls.append((review_id, reviewer_id))
        return {
            "review_id": review_id,
            "brief": "One storyboard shot",
            "shot_spec": {"camera_angle": "wide", "duration_seconds": 5},
            "assets": [{
                "asset_id": "asset-1",
                "label": "Shot reference",
                "media_type": "image/png",
                "uri": "https://assets.example.test/shot.png",
                "alt_text": "Storyboard reference",
            }],
        }

    app = FastAPI()
    app.include_router(create_review_context_router(
        load_review_context=load_review_context,
        authenticate_reviewer=lambda: "reviewer-1",
    ))
    response = TestClient(app).get("/reviews/review-1/context")

    assert response.status_code == 200
    assert response.json()["shot_spec"]["camera_angle"] == "wide"
    assert response.json()["assets"][0]["asset_id"] == "asset-1"
    assert calls == [("review-1", "reviewer-1")]


def test_review_context_missing_returns_404():
    app = FastAPI()
    app.include_router(create_review_context_router(
        load_review_context=lambda **_: None,
        authenticate_reviewer=lambda: "reviewer-1",
    ))
    assert TestClient(app).get("/reviews/missing/context").status_code == 404


def test_review_context_rejects_mismatched_review_id():
    app = FastAPI()
    app.include_router(create_review_context_router(
        load_review_context=lambda **_: {"review_id": "other", "shot_spec": {}, "assets": []},
        authenticate_reviewer=lambda: "reviewer-1",
    ))
    assert TestClient(app).get("/reviews/review-1/context").status_code == 404

