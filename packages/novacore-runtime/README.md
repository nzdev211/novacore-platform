# novacore-runtime

Runtime coordination layer for Novacore Platform.

**Status: contract-design stage.** The package intentionally does not yet contain executable orchestration or provider/database implementations.

## Responsibilities

- Coordinate Planner, AssignmentEngine, and Executor.
- Define application-facing ports required by concrete Runtime use cases.
- Coordinate Work, Assignment, Worker, and Execution lifecycle through Kernel domain objects.
- Keep vendor SDKs, HTTP frameworks, and database drivers outside Runtime.

## Dependency rules

- Runtime may depend on the public Kernel API and Foundation where genuinely required.
- Runtime must not depend on OpenAI, Anthropic, Google ADK, FastAPI, Firestore, or PostgreSQL SDKs.
- Concrete adapters implement ports owned by Runtime/application boundaries.
- Kernel must never import Runtime.

## Current implementation gate

Before executable ports are frozen, reconcile the legacy Kernel modules in the repository snapshot with the approved v0.1 domain schema (`Context`, `Activity`, `Objective`, `Planning`, `Work`, `Contract`, `Worker`, `Assignment`, and `Execution`). Do not build repository interfaces against legacy entity shapes.

