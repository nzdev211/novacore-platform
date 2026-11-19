"""ASGI entry point: novacore_server.main:app."""

from .app import create_app

app = create_app()

