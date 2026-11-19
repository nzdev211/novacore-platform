"""Novacore Platform application server."""

from .app import create_app
from .config import ServerSettings

__all__ = ["ServerSettings", "create_app"]

