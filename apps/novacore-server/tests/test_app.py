from fastapi.testclient import TestClient

from novacore_server.app import create_app
from novacore_server.config import ServerSettings


def test_app_factory_creates_application_without_connecting_infrastructure():
    settings = ServerSettings(app_name="Novacore Test", environment="test")
    app = create_app(settings)

    assert app.title == "Novacore Test"
    assert app.state.settings is settings
    # Phase 40 intentionally has no business/API routes yet.
    assert {route.path for route in app.routes} >= {"/openapi.json", "/docs"}


def test_openapi_is_available():
    app = create_app(ServerSettings(environment="test"))
    response = TestClient(app).get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["title"] == "Novacore Platform"
