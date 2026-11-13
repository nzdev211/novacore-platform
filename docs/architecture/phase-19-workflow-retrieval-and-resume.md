# Phase 19 — Workflow Retrieval and Resume

## Objective

Allow a Creative Studio application to reopen a persisted workflow after a browser refresh, process restart, or user return. Runtime's `WorkflowStore` port now includes `load_workflow(ActivityId)`, returning a `WorkflowSnapshot` or `None` when the Activity does not exist.

## Design boundaries

- Kernel domain objects and their attributes are unchanged.
- Runtime defines the provider-independent `WorkflowSnapshot` and persistence contract.
- `novacore-firestore` reconstructs domain records from Firestore documents.
- Google ADK session persistence remains separate and continues to own ADK sessions/events/state.
- Loading a workflow is read-only and never invokes an agent.

## Loaded records

The snapshot includes Request, Context, Objective, Activity, all Planning and Work records for the Activity, their Contracts and Assignments, and the Executions associated with those Assignments.

## Important limitation

This phase restores the persisted business records so the application can reopen the workflow and continue its own user-facing flow. It does not automatically retry or resume an interrupted provider call. Execution currently has identity only; there is no persisted execution lifecycle state, result payload, idempotency key, or retry policy in the approved v0.1 Kernel. Those require a separately agreed Runtime-level execution lifecycle design. Never blindly re-run an Execution just because it appears in a loaded snapshot.

## Consistency

The initial records remain atomically written by the existing Firestore transaction. Execution identities remain separate writes before external invocation. Reads are multiple Firestore document/query reads and are not a cross-collection snapshot transaction; callers should treat this as a rehydration view, not a globally consistent point-in-time snapshot under concurrent mutation.

