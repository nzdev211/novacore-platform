import pytest

from novacore_server.config import ServerSettings


def test_defaults(monkeypatch):
    for key in (
        "NOVACORE_APP_NAME", "NOVACORE_ENVIRONMENT", "NOVACORE_HOST",
        "NOVACORE_PORT", "NOVACORE_LOG_LEVEL", "NOVACORE_CORS_ORIGINS",
    ):
        monkeypatch.delenv(key, raising=False)

    settings = ServerSettings.from_env()

    assert settings.app_name == "Novacore Platform"
    assert settings.host == "127.0.0.1"
    assert settings.port == 8000
    assert settings.cors_origins == ()


def test_environment_values_and_multiple_cors_origins(monkeypatch):
    monkeypatch.setenv("NOVACORE_ENVIRONMENT", "test")
    monkeypatch.setenv("NOVACORE_PORT", "8123")
    monkeypatch.setenv("NOVACORE_CORS_ORIGINS", "http://localhost:3000, https://studio.example.com/")

    settings = ServerSettings.from_env()

    assert settings.environment == "test"
    assert settings.port == 8123
    assert settings.cors_origins == ("http://localhost:3000", "https://studio.example.com")


@pytest.mark.parametrize("value", ["zero", "0", "65536"])
def test_invalid_port_is_rejected(monkeypatch, value):
    monkeypatch.setenv("NOVACORE_PORT", value)
    with pytest.raises(ValueError):
        ServerSettings.from_env()


def test_invalid_log_level_is_rejected(monkeypatch):
    monkeypatch.setenv("NOVACORE_LOG_LEVEL", "verbose-ish")
    with pytest.raises(ValueError):
        ServerSettings.from_env()

