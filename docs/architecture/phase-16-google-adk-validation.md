# Phase 16 — Google ADK Integration Validation

## Objective

Make the Phase 15 Creative Studio integration operationally verifiable without
changing the Kernel or Runtime architecture.

## Phase 16 scope

- Google ADK environment preflight script.
- Live-run configuration and troubleshooting guide.
- Explicit separation between offline automated tests and live provider
  validation.
- Documentation of the in-memory ADK session default and demo persistence
  limitations that existed at the time of Phase 16.

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
Google ADK Runner + SessionService
        |
        v
Gemini model endpoint
```

## Decisions preserved

- One Kernel, one Runtime, independent adapters.
- Kernel and Runtime contracts unchanged by Phase 16.
- Google ADK remains an adapter.
- Runtime v0.1 `AgentExecutor` remains synchronous; the adapter bridges to
  ADK's asynchronous `Runner.run_async`.
- In-memory ADK sessions remain the default unless another backend is selected.
- Runtime workflow persistence and ADK session persistence are separate
  responsibilities.

## Validation status at Phase 16

The Phase 16 automated tests validated deterministic behavior using local test
fakes. They did not make a live Gemini request. Live validation requires the
user to install the Google ADK extra, configure Google AI Studio or Vertex AI
credentials, and run the example described in
`docs/operations/google-adk-validation.md`.

## Follow-up implementation status

The following items were deferred in Phase 16 and implemented in later phases:

| Capability | Implemented in | Current responsibility |
|---|---:|---|
| Durable Runtime workflow persistence | Phase 17 | `novacore-firestore` implements Runtime `WorkflowStore` |
| Firestore-backed ADK sessions | Phase 18 | `novacore-google-adk` uses Google's official `FirestoreSessionService` |
| Workflow retrieval and resume | Phase 19 | Runtime `WorkflowStore` retrieval and workflow snapshot |
| Execution lifecycle and recovery inspection | Phase 20 | Runtime execution lifecycle and recovery services |
| Idempotency reservation and recovery decisions | Phase 21 | Runtime policy with Firestore-backed persistence safeguards |

These later capabilities do not change the Kernel domain model. ADK session
state remains distinct from Novacore business workflow records and execution
lifecycle records.

## Current boundaries

- Kernel contains provider-independent domain concepts only.
- Runtime owns business workflow orchestration and execution lifecycle policy.
- `novacore-google-adk` adapts Runtime `AgentExecutor` to Google ADK.
- `novacore-firestore` persists Runtime workflow and execution records.
- Google's official ADK Firestore session service persists ADK sessions and
  events; it is not a replacement for Runtime `WorkflowStore`.

## Live validation limitation

Automated tests and a successful local preflight do not prove that a live
provider request will succeed. A live run must be performed in an environment
with valid credentials, network access, and an available configured model.

