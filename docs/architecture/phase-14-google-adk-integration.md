# Phase 14 — Google ADK Integration

## Decision

`novacore-google-adk` implements Runtime's existing `AgentExecutor` port. In-memory session service is the default. A caller may inject a custom ADK session service for durable storage.

## Boundaries

- Kernel and Runtime contracts remain unchanged.
- ADK Runner, sessions, events and GenAI message types stay inside the adapter.
- ADK owns agent execution; Runtime owns business workflow orchestration.
- Firestore-backed session persistence is an extension point only; it is not implemented in this phase.

## Request mapping

| Runtime value | ADK mapping |
|---|---|
| `execution_id.value` | `session_id` |
| `worker_id.value` + prefix | `user_id` |
| Assignment/execution/worker IDs and input | JSON user message |
| Latest non-empty event text | `AgentExecutionResult.output["text"]` |

## Deferred

Firestore service implementation, artifact/media storage, streaming, cancellation, retries, human-review resume, and output persistence.

