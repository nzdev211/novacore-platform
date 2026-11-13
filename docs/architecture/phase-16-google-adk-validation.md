# Phase 16 — Google ADK Integration Validation

## Objective

Make the Phase 15 Creative Studio integration operationally verifiable without
changing the Kernel or Runtime architecture.

## Included

- Google ADK environment preflight script.
- Live-run configuration and troubleshooting guide.
- Explicit separation between offline automated tests and live provider
  validation.
- Documented in-memory session and demo persistence limitations.

## Architecture

```text
Creative Studio Example
        |
        v
StoryboardWorkflowService (Runtime)
        |
        v
AgentExecutor port
        |
        v
GoogleADKAgentExecutor
        |
        v
Google ADK Runner + InMemorySessionService
        |
        v
Gemini model endpoint
```

## Decisions preserved

- One Kernel, one Runtime, independent adapters.
- Kernel and Runtime contracts unchanged.
- Google ADK remains an adapter.
- Runtime v0.1 `AgentExecutor` remains synchronous; adapter bridges to ADK's
  asynchronous `Runner.run_async`.
- In-memory ADK sessions remain the default.
- Custom ADK session service injection remains the persistence extension point.
- Firestore session persistence is not claimed until its ADK service contract
  implementation and integration tests exist.
- Demo workflow persistence remains in-memory.

## Validation

The test suite verifies the deterministic behavior of Kernel, Runtime, and the
Google ADK adapter using local tests. The live Gemini call requires the user to
install Google ADK, configure credentials, and run the example as described in
`docs/operations/google-adk-validation.md`.

## Deferred

- Firestore implementation of ADK `BaseSessionService`.
- Durable Firestore/PostgreSQL implementation of Runtime `WorkflowStore`.
- Production worker directory.
- Streaming, cancellation, progress callbacks, artifact storage, human review,
  and execution retry policies.

