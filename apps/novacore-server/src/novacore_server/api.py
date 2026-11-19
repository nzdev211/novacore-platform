"""HTTP API registration for the Novacore Platform server.

The server registers existing FastAPI adapter routers. Authentication,
resource authorization, and Creative Studio-specific context/history loaders
remain host-provided dependencies; safe defaults fail closed.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


def _unconfigured_dependency(name: str) -> Callable[..., Any]:
    def dependency() -> Any:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail=f"Host integration '{name}' is not configured.")
    dependency.__name__ = f"unconfigured_{name}"
    return dependency


def _unconfigured_callback(name: str) -> Callable[..., Any]:
    def callback(**_: Any) -> Any:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail=f"Host integration '{name}' is not configured.")
    return callback


@dataclass(frozen=True, slots=True)
class ApiDependencies:
    """Host-owned integrations required by authenticated API routes.

    Authentication dependencies must return a stable authenticated principal
    ID and enforce the host's authentication policy. Callbacks for context and
    history must additionally enforce resource/tenant authorization.
    """
    authenticate_reviewer: Callable[..., str] | None = None
    authenticate_creator: Callable[..., str] | None = None
    load_review_context: Callable[..., Any] | None = None
    load_revision_history: Callable[..., Any] | None = None
    create_revision: Callable[..., Any] | None = None


def register_api(app: Any, dependencies: ApiDependencies | None = None) -> None:
    """Register health endpoints and the existing review-related routers."""
    from fastapi import APIRouter, HTTPException
    from novacore.fastapi import (
        create_human_review_router,
        create_review_context_router,
        create_revision_history_router,
        create_revision_router,
    )

    deps = dependencies or ApiDependencies()
    reviewer_auth = deps.authenticate_reviewer or _unconfigured_dependency("authenticate_reviewer")
    creator_auth = deps.authenticate_creator or _unconfigured_dependency("authenticate_creator")
    context_loader = deps.load_review_context or _unconfigured_callback("load_review_context")
    history_loader = deps.load_revision_history or _unconfigured_callback("load_revision_history")
    revision_creator = deps.create_revision or _unconfigured_callback("create_revision")

    system = APIRouter(tags=["platform"])

    @system.get("/", summary="Platform information")
    def root() -> dict[str, str]:
        return {"name": app.title, "version": app.version, "status": "running"}

    @system.get("/health", summary="Liveness probe")
    def health() -> dict[str, str]:
        # Liveness deliberately does not depend on Firestore or external agents.
        return {"status": "ok"}

    @system.get("/ready", summary="Readiness probe")
    def ready() -> dict[str, str]:
        # This confirms composition completed, not that every remote dependency
        # is reachable. A future infrastructure probe can strengthen readiness.
        if getattr(app.state, "container", None) is None:
            raise HTTPException(status_code=503, detail="Platform dependencies are not initialized.")
        return {"status": "ready"}

    app.include_router(system)

    app.include_router(create_human_review_router(
        review_service=_review_service_from_app(app),
        review_store=_review_store_from_app(app),
        authenticate_reviewer=reviewer_auth,
    ))
    app.include_router(create_review_context_router(
        load_review_context=context_loader,
        authenticate_reviewer=reviewer_auth,
    ))
    app.include_router(create_revision_history_router(
        load_revision_history=history_loader,
        authenticate_reviewer=reviewer_auth,
    ))
    app.include_router(create_revision_router(
        create_revision=revision_creator,
        authenticate_creator=creator_auth,
    ))


def _review_service_from_app(app: Any) -> Any:
    """Resolve the Runtime service at request time, after lifespan startup."""
    class ServiceProxy:
        def submit_for_review(self, record: Any) -> Any:
            container = getattr(app.state, "container", None)
            if container is None:
                raise RuntimeError("Platform dependencies are not initialized.")
            return container.human_review_service.submit_for_review(record)

        def decide(self, *args: Any, **kwargs: Any) -> Any:
            container = getattr(app.state, "container", None)
            if container is None:
                raise RuntimeError("Platform dependencies are not initialized.")
            return container.human_review_service.decide(*args, **kwargs)

    return ServiceProxy()


def _review_store_from_app(app: Any) -> Any:
    class StoreProxy:
        def load_review(self, review_id: str) -> Any:
            container = getattr(app.state, "container", None)
            if container is None:
                raise RuntimeError("Platform dependencies are not initialized.")
            return container.review_store.load_review(review_id)
    return StoreProxy()

