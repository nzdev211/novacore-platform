"""FastAPI application factory and application-lifecycle composition."""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator, Callable, Any

from .config import ServerSettings
from .api import ApiDependencies, register_api


def create_app(
    settings: ServerSettings | None = None,
    *,
    container_factory: Callable[..., Any] | None = None,
    agent_factory: Callable[[ServerSettings], Any] | None = None,
    firestore_client: Any | None = None,
    session_service: Any | None = None,
    api_dependencies: ApiDependencies | None = None,
):
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
    except ImportError as exc:
        raise ImportError("Install novacore-server[server] to run the Novacore HTTP server.") from exc

    resolved_settings = settings or ServerSettings.from_env()
    if container_factory is None:
        from .container import build_container
        container_factory = build_container

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        container = container_factory(
            resolved_settings,
            firestore_client=firestore_client,
            agent_factory=agent_factory,
            session_service=session_service,
        )
        app.state.container = container
        try:
            yield
        finally:
            close = getattr(container, "close", None)
            try:
                if callable(close):
                    close()
            finally:
                app.state.container = None

    app = FastAPI(
        title=resolved_settings.app_name,
        version="0.1.0",
        description="Novacore Platform HTTP API",
        lifespan=lifespan,
    )
    app.state.settings = resolved_settings
    app.state.container = None
    if resolved_settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=list(resolved_settings.cors_origins),
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            allow_headers=["Authorization", "Content-Type", "Cookie", "Idempotency-Key"],
        )
    register_api(app, api_dependencies)
    return app

