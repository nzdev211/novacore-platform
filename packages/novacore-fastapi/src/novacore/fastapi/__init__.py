"""FastAPI inbound adapter namespace for Novacore."""

from .reviews import create_human_review_router

__all__ = ["create_human_review_router"]

