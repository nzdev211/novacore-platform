# Phase 41 — Dependency Injection and Adapter Assembly

## Result

The server now has a composition root (`novacore_server.container`) and creates
one shared Firestore client for `FirestoreWorkflowStore`, `FirestoreReviewStore`,
and `FirestoreRevisionRecordStore`. It constructs `HumanReviewService` from
`FirestoreReviewStore`. When a host-supplied ADK agent factory is configured,
it constructs `GoogleADKAgentExecutor` and `AgentRevisionExecutionPort`.

The FastAPI application owns container startup/shutdown through its lifespan.
The Firestore client is closed when the application shuts down.

## Agent configuration

`NOVACORE_ADK_AGENT_FACTORY` uses `package.module:callable` syntax. The factory
receives `ServerSettings` and returns a real, configured Google ADK Agent. This
is intentionally host-supplied: the platform has not agreed a universal agent
instruction, model, or storyboard-specific agent implementation.

## Repository consistency finding

The current Runtime `services/__init__.py` imports `execution_recovery` and
`revision_workflow`, but those Python modules are absent from the current
Runtime services directory listing. That makes importing the services package
fail. This patch corrects the package exports to include only the modules that
are actually present, including `human_review` and `revision_execution`.

`RevisionWorkflowService` cannot be assembled until its implementation is
restored. Phase 42 must not pretend the revision endpoint is fully wired until
that dependency and the host authorization/input callbacks exist.

## Not included

- API router registration (Phase 42)
- Authentication provider or tenant authorization
- Review context/history resolver implementations
- Firestore ADK session persistence (ADK session backend remains memory unless
  a custom session service is supplied)
- A product-specific Google ADK Agent
- Production secrets/deployment configuration

