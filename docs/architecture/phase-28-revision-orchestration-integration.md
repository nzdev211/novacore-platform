# Phase 28 — Revision Orchestration Integration

## Goal

Move the Phase 26 revision endpoint beyond a host callback placeholder by
providing a Runtime-owned orchestration service and explicit adapter ports.

## Flow

1. The FastAPI route authenticates the creator and passes the identity to
   `RevisionWorkflowService`.
2. `RevisionSourceStore` loads the requested review and its exact source
   execution after tenant/resource authorization.
3. Runtime requires `CHANGES_REQUESTED`.
4. `RevisionExecutionPort` delegates to the normal execution path. The adapter
   must create a new Kernel Execution identity and use Phase 20–21 lifecycle
   and idempotency behavior.
5. `RevisionReviewCreator` creates a new `PENDING` review linked to the new
   execution and the source review.
6. `RevisionRecordStore` stores the source-review/idempotency-key relationship.

## Boundaries

- No Kernel changes.
- Runtime does not import FastAPI, Firestore, Google ADK, or provider SDKs.
- Runtime does not generate identifiers; the execution adapter/host supplies
  identities according to the established caller-supplied ID policy.
- The old Execution, output, assets, ReviewRecord, and feedback are immutable.
- The new ReviewRecord points to the new Execution and same Activity/Work.
- The execution adapter must pass source brief, source output, review feedback,
  and additional instructions into the new agent request.
- The new execution is not automatically retried if its status is uncertain.
- Only a succeeded execution may be submitted for human review.

## Idempotency and atomicity

The service first atomically reserves `(source_review_id, idempotency_key)`.
A completed result is replayed; an in-progress key is rejected by the adapter.
A simple read-then-write implementation is not sufficient under concurrent
requests. If validation fails before execution starts, the reservation is
released. Once execution starts, it is retained for reconciliation rather than
allowing a second provider call.
The Runtime service deliberately does not claim exactly-once provider execution.
If a process crashes after execution succeeds but before review/lineage commit,
the adapter must reconcile the persisted execution and finish review creation
without calling the provider again.

## Adapter responsibilities

- `RevisionSourceStore`: authorization, exact source review/execution lookup.
- `RevisionExecutionPort`: create and persist new Execution; call existing
  AgentExecutor; persist lifecycle and output; honor idempotency.
- `RevisionReviewCreator`: create a new PENDING ReviewRecord; retain
  `source_review_id` lineage.
- `RevisionRecordStore`: atomic key reservation and result persistence.

The Phase 28 service is a coordination layer, not a Firestore implementation.
A Firestore adapter must be implemented against the actual deployed schema
before claiming end-to-end persistence.

## Not included

- No Firestore schema migration or concrete Firestore adapter.
- No direct Google ADK invocation.
- No automatic Activity completion.
- No changes to Phase 22 ReviewRecord fields or Kernel entities.

