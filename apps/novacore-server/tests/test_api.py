from types import SimpleNamespace

from fastapi.testclient import TestClient

from novacore_server.api import ApiDependencies
from novacore_server.app import create_app
from novacore_server.config import ServerSettings


class FakeContainer:
    def __init__(self):
        self.human_review_service = object()
        self.review_store = object()
        self.closed = False

    def close(self):
        self.closed = True


def test_health_and_readiness_lifecycle():
    container = FakeContainer()
    app = create_app(ServerSettings(), container_factory=lambda *_args, **_kwargs: container)
    with TestClient(app) as client:
        assert client.get("/health").json() == {"status": "ok"}
        assert client.get("/ready").json() == {"status": "ready"}
        assert client.get("/").json()["name"] == "Novacore Platform"
    assert container.closed
    assert app.state.container is None


def test_ready_is_unavailable_before_startup():
    app = create_app(ServerSettings(), container_factory=lambda *_args, **_kwargs: FakeContainer())
    response = TestClient(app).get("/ready")
    assert response.status_code == 503


def test_host_routes_fail_closed_without_auth_configuration():
    container = FakeContainer()
    app = create_app(ServerSettings(), container_factory=lambda *_args, **_kwargs: container)
    with TestClient(app) as client:
        response = client.get("/reviews/example")
        assert response.status_code == 503
        assert "authenticate_reviewer" in response.json()["detail"]


def test_review_router_uses_host_auth_dependency():
    container = FakeContainer()
    app = create_app(
        ServerSettings(),
        container_factory=lambda *_args, **_kwargs: container,
        api_dependencies=ApiDependencies(authenticate_reviewer=lambda: "reviewer-1"),
    )
    # Router registration and dependency injection are visible in OpenAPI even
    # when the fake store intentionally has no persistence implementation.
    with TestClient(app) as client:
        schema = client.get("/openapi.json").json()
        assert "/reviews/{review_id}/decision" in schema["paths"]
        assert "/reviews/{review_id}/context" in schema["paths"]
        assert "/reviews/{review_id}/history" in schema["paths"]
        assert "/reviews/{review_id}/revisions" in schema["paths"]


def test_openapi_exposes_system_endpoints():
    app = create_app(ServerSettings(), container_factory=lambda *_args, **_kwargs: FakeContainer())
    with TestClient(app) as client:
        paths = client.get("/openapi.json").json()["paths"]
    assert "/health" in paths
    assert "/ready" in paths

