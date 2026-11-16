# Phase 34 — Production Revision Workflow Wiring

## Goal

Connect the existing revision workflow to the normal Runtime execution lifecycle. Preserve the Kernel schema and keep provider SDKs outside Kernel and Runtime contracts.

## Changes

- `AgentRevisionExecutionPort` implements the Runtime `RevisionExecutionPort` using the existing `WorkflowStore` and `AgentExecutor` ports.
- The source review's Assignment and Worker identities are loaded with the exact reviewed Execution. A revision reuses that Assignment and creates a new Execution identity.
- The host supplies `create_execution_id`; Runtime does not generate Kernel identifiers.
- The adapter persists the new Execution identity, then PENDING, RUNNING, and SUCCEEDED/FAILED lifecycle records. The agent is invoked only after PENDING and RUNNING are persisted.
- The agent input preserves the original execution input and adds `revision_context` containing the source execution ID, original output, reviewer feedback, and additional instructions.
- Google ADK remains an implementation of the existing `AgentExecutor` port. Runtime does not import Google ADK.
- Firestore query construction uses `FieldFilter` rather than positional `where` arguments to avoid the SDK deprecation warning.

## Runtime flow

1. FastAPI authenticates the creator and calls `RevisionWorkflowService`.
2. `FirestoreRevisionRecordStore` atomically reserves the `(source_review_id, idempotency_key)` pair.
3. `FirestoreRevisionSourceStore` authorizes the creator and loads the exact reviewed execution, its Assignment/Worker, original input, output, and feedback.
4. `AgentRevisionExecutionPort` creates a new Execution ID supplied by the host and reuses the original Assignment.
5. The Runtime adapter persists lifecycle state and invokes the injected `AgentExecutor` (for example, `GoogleADKAgentExecutor`).
6. `StoreRevisionReviewCreator` creates a new PENDING review for the successful execution.
7. The revision reservation is completed with the new execution and review IDs.

## Failure and recovery

- Before the external execution begins, the revision service may release its reservation.
- Once execution begins, the reservation is retained on failure. Do not blindly retry an uncertain provider call.
- Provider exceptions are recorded as FAILED when the lifecycle store remains available, then propagated.
- If persisting a lifecycle transition fails, the revision reservation remains for operator reconciliation.
- This does not guarantee exactly-once provider execution. Provider-side idempotency support is still required for that guarantee.

## Boundaries

- No Kernel changes.
- No new aggregate root or domain lifecycle behavior.
- No automatic ID generation inside Kernel or Runtime.
- No production authentication, tenant policy, or resource authorization implementation; the host application supplies these.
- No automatic retry or expiry of uncertain revision reservations.
- No real provider call is made by the tests; the AgentExecutor is a test double.

