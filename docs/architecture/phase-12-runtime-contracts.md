# Phase 12 — Runtime Contract Implementation

## Objective

Turn the Phase 11 Creative Studio workflow into a minimal executable set of Runtime-owned Python protocols and DTOs, without importing infrastructure SDKs.

## Implemented ports

| Port | Responsibility |
|---|---|
| `ModelGenerator` | One bounded direct model-generation request/response |
| `AgentExecutor` | One agent-framework execution attempt |
| `WorkerDirectory` | Find workers satisfying required capabilities and resolve capabilities |
| `WorkflowStore` | Atomically persist initial workflow records; persist an Execution before worker invocation |

## Boundary decisions

- Model generation and agent execution are separate ports.
- Kernel identity types are reused; Runtime does not generate IDs.
- Kernel entities remain unchanged.
- Provider-specific configuration stays in adapter composition/configuration.
- Provider exceptions are translated to Runtime boundary errors by adapters.
- `WorkflowStore.save_initial_workflow` is an atomic application operation.
- `save_execution` is called before invoking a worker.
- No database transaction remains open during model calls or human review.
- Large media remains external; this phase does not define blob storage.
- Protocols are synchronous for v0.1. Async, streaming, cancellation, and progress events are deferred until required by a concrete adapter/use case.

## Known limitations / next design gates

- The shot-package output schema and acceptance checklist remain product decisions.
- Human review decisions and resumable workflow state need a dedicated Runtime persistence design before production.
- Resource storage is not implemented.
- Revision semantics (reuse Work vs create new Work) remain open.
- The `WorkflowStore` method is intentionally use-case-specific; do not generalize to CRUD repositories prematurely.

## Verification

The Runtime package is dependency-free apart from the Kernel package at the Python import boundary. Unit tests cover DTO validation and protocol shape. Adapter implementations and SDK calls are out of scope.

