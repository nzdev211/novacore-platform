"""Command-line entry point for local Novacore server execution."""

from __future__ import annotations


def main() -> None:
    try:
        import uvicorn
    except ImportError as exc:
        raise SystemExit("Install novacore-server[server] before starting the server.") from exc

    from .config import ServerSettings

    settings = ServerSettings.from_env()
    uvicorn.run(
        "novacore_server.main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level,
        reload=settings.environment == "development",
    )

