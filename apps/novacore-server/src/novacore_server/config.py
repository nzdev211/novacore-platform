"""Environment-backed settings for the Novacore Platform server.

This module deliberately uses the Python standard library. Configuration
must not introduce a dependency into Kernel or Runtime.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


def _parse_origins(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    return tuple(origin.strip().rstrip("/") for origin in value.split(",") if origin.strip())


@dataclass(frozen=True, slots=True)
class ServerSettings:
    app_name: str = "Novacore Platform"
    environment: str = "development"
    host: str = "127.0.0.1"
    port: int = 8000
    log_level: str = "info"
    cors_origins: tuple[str, ...] = ()

    @classmethod
    def from_env(cls) -> "ServerSettings":
        """Load settings from NOVACORE_* environment variables."""
        raw_port = os.getenv("NOVACORE_PORT", "8000")
        try:
            port = int(raw_port)
        except ValueError as exc:
            raise ValueError("NOVACORE_PORT must be an integer.") from exc
        if not 1 <= port <= 65535:
            raise ValueError("NOVACORE_PORT must be between 1 and 65535.")

        environment = os.getenv("NOVACORE_ENVIRONMENT", "development").strip()
        if not environment:
            raise ValueError("NOVACORE_ENVIRONMENT cannot be empty.")

        log_level = os.getenv("NOVACORE_LOG_LEVEL", "info").strip().lower()
        if log_level not in {"critical", "error", "warning", "info", "debug", "trace"}:
            raise ValueError("NOVACORE_LOG_LEVEL must be a supported logging level.")

        return cls(
            app_name=os.getenv("NOVACORE_APP_NAME", "Novacore Platform").strip(),
            environment=environment,
            host=os.getenv("NOVACORE_HOST", "127.0.0.1").strip(),
            port=port,
            log_level=log_level,
            cors_origins=_parse_origins(os.getenv("NOVACORE_CORS_ORIGINS")),
        )

