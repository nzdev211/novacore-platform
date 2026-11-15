# Phase 30 — Revision Source and Execution Integration

## Goal

Connect Phase 28's Runtime revision orchestration to the existing Phase 21 workflow/execution stores and Phase 22 human-review store without changing Kernel entities or duplicating the execution lifecycle.

## Added components

- `FirestoreRevisionSourceStore` loads the review, checks host-provided resource authorization, loads the Activity workflow, resolves the exact Execution referenced by the review, verifies its Assignment belongs to the reviewed Work, and loads its persisted lifecycle output.
- `StoreRevisionReviewCreator` creates a new `PENDING` review through the existing `ReviewStore` port.
- `CallbackRevisionExecutionPort` bridges the revision service to the application's existing Runtime execution path. The callback must create a new Execution and use the normal execution lifecycle/idempotency contracts.

## Why two host callbacks remain required

The approved `ReviewRecord` schema has no tenant/owner field, and the v0.1 workflow schema does not persist a canonical copy of every `AgentExecutionRequest.input`. Therefore the adapter requires:

1. `authorize(creator_id, activity_id, work_id) -> bool`
2. `load_execution_input(activity_id, execution_id) -> Mapping`

These are explicit host integration seams, not guessed fields or implicit access rules. The input loader must retrieve the original input for the exact reviewed Execution; it must not substitute the latest Activity brief or another execution's input.

The execution callback must invoke the existing Runtime execution path, create a distinct Execution ID, persist `PENDING -> RUNNING -> SUCCEEDED/FAILED` lifecycle state using `WorkflowStore`, and pass the same idempotency key through to the execution layer. It must not call Google ADK or another provider directly from the Firestore package.

## Revision sequence

1. Phase 29 atomically reserves `(source_review_id, idempotency_key)`.
2. Source adapter loads and authorizes the source review and exact source Execution.
3. Runtime rejects any source review other than `CHANGES_REQUESTED`.
4. Execution adapter delegates to the normal Runtime execution lifecycle and returns a new successful Execution.
5. Review creator writes a new `PENDING` ReviewRecord for that new Execution.
6. Phase 29 marks the revision attempt complete with the new Execution and Review IDs.

The original Execution and Review are never overwritten.

## Failure and recovery

A reservation is retained once execution may have started. If execution succeeds but creation of the new review or completion of the revision record fails, the attempt remains reserved and requires reconciliation. Do not release it or automatically invoke the provider again. Phase 29's reservation is not an exactly-once provider guarantee; provider-side idempotency remains necessary to protect against duplicate external work/billing.

## Out of scope

- No Kernel changes or new domain entities.
- No tenant/authentication implementation; host supplies authorization.
- No invented execution-input persistence schema.
- No concrete ADK worker binding or provider invocation in the Firestore adapter.
- No automatic retry/reconciliation job.

