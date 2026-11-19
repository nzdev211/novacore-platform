# Phase 41 Patch Manifest

Apply this patch on top of Phase 40 at the `novacore-platform` repository root.

## Added
- `apps/novacore-server/src/novacore_server/container.py`
- `apps/novacore-server/tests/test_container.py`
- `docs/operations/phase-41-dependency-injection.md`

## Replaced
- `apps/novacore-server/src/novacore_server/config.py`
- `apps/novacore-server/src/novacore_server/app.py`
- `apps/novacore-server/src/novacore_server/cli.py`
- `apps/novacore-server/.env.example`
- `apps/novacore-server/pyproject.toml`
- `apps/novacore-server/README.md`
- `apps/novacore-server/tests/test_app.py`
- `packages/novacore-runtime/src/novacore/runtime/services/__init__.py`

No Kernel domain classes or Runtime port contracts are changed.

