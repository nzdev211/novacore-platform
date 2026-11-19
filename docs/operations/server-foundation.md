# Phase 40 — Novacore Server Foundation

## Goal

Establish a runnable FastAPI application host without changing the approved Kernel, Runtime, or adapter architecture.

## Added package

`apps/novacore-server`

- `config.py`: standard-library environment configuration and validation.
- `app.py`: FastAPI application factory and lifespan boundary.
- `main.py`: ASGI import target (`novacore_server.main:app`).
- `cli.py`: `novacore-server` local startup command.
- `.env.example`: documented local settings.

## Deliberate non-goals

- No Runtime or adapter construction yet.
- No Firestore or Google ADK client initialization.
- No authentication provider implementation.
- No business API routers or health endpoints.
- No changes to Kernel or Runtime.

## Next phase

Phase 41 will define the application composition and dependency injection that instantiate existing adapters and Runtime services. Do not put provider SDK setup into `main.py` or import adapters into Kernel/Runtime.

