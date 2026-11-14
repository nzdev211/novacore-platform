"""FastAPI adapters for Novacore."""

from novacore.fastapi.review_context import create_review_context_router
from novacore.fastapi.reviews import create_human_review_router
from novacore.fastapi.revision_history import create_revision_history_router
from novacore.fastapi.revisions import create_revision_router

__all__ = [
    "create_human_review_router",
    "create_review_context_router",
    "create_revision_router",
    "create_revision_history_router",
]


