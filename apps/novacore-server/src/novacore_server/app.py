"""FastAPI application factory for the Novacore Platform server."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from .config import ServerSettings


def create_app(settings: ServerSettings | None = None):
    """Create the HTTP application without constructing infrastructure.

    Adapter and Runtime construction is intentionally deferred to Phase 41.
    This keeps application creation deterministic and avoids hidden network
    connections during module import or test discovery.
    """
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
    except ImportError as exc:
        raise ImportError(
            "Install novacore-server[server] to run the Novacore HTTP server."
        ) from exc

    resolved_settings = settings or ServerSettings.from_env()

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        # Phase 41 will initialize and close injected adapter resources here.
        yield

    app = FastAPI(
        title=resolved_settings.app_name,
        version="0.1.0",
        description="Novacore Platform HTTP API",
        lifespan=lifespan,
    )
    app.state.settings = resolved_settings

    if resolved_settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=list(resolved_settings.cors_origins),
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            allow_headers=["Authorization", "Content-Type", "Cookie", "Idempotency-Key"],
        )

    @app.get("/health", tags=["ops"])
    def health():
        return {
            "status": "ok",
            "app": resolved_settings.app_name,
            "environment": resolved_settings.environment,
        }

    @app.get("/", tags=["ops"])
    def root():
        return {
            "name": resolved_settings.app_name,
            "version": "0.1.0",
            "docs": "/docs",
            "health": "/health",
        }

    return app
