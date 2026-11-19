"""Keep server tests independent of separately-installed Novacore packages.

The actual adapter factories are exercised in their own package test suites.
These minimal router factories let this app package test registration and
lifecycle behavior without importing the full workspace.
"""
import sys
import types

from fastapi import APIRouter, Depends, HTTPException


def _auth():
    raise HTTPException(status_code=503, detail="Host integration 'authenticate_reviewer' is not configured.")


def _creator_auth():
    raise HTTPException(status_code=503, detail="Host integration 'authenticate_creator' is not configured.")


def _review_router(*, review_service, review_store, authenticate_reviewer):
    router = APIRouter(prefix="/reviews")

    @router.get("/{review_id}")
    def get_review(review_id: str, _principal=Depends(authenticate_reviewer)):
        return {"review_id": review_id}

    @router.post("/{review_id}/decision")
    def decide(review_id: str, _principal=Depends(authenticate_reviewer)):
        return {"review_id": review_id}
    return router


def _context_router(*, load_review_context, authenticate_reviewer):
    router = APIRouter(prefix="/reviews")

    @router.get("/{review_id}/context")
    def context(review_id: str, _principal=Depends(authenticate_reviewer)):
        return load_review_context(review_id=review_id)
    return router


def _history_router(*, load_revision_history, authenticate_reviewer):
    router = APIRouter(prefix="/reviews")

    @router.get("/{review_id}/history")
    def history(review_id: str, _principal=Depends(authenticate_reviewer)):
        return load_revision_history(review_id=review_id)
    return router


def _revision_router(*, create_revision, authenticate_creator):
    router = APIRouter(prefix="/reviews")

    @router.post("/{review_id}/revisions")
    def revision(review_id: str, _principal=Depends(authenticate_creator)):
        return create_revision(source_review_id=review_id)
    return router


module = types.ModuleType("novacore.fastapi")
module.create_human_review_router = _review_router
module.create_review_context_router = _context_router
module.create_revision_history_router = _history_router
module.create_revision_router = _revision_router
package = types.ModuleType("novacore")
package.__path__ = []
sys.modules.setdefault("novacore", package)
sys.modules["novacore.fastapi"] = module

