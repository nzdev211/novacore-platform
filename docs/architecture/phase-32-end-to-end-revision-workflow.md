# Phase 32 — End-to-End Revision Workflow

## Goal

Verify the complete revision request path from the FastAPI boundary through Runtime orchestration and back to a newly created pending review. This phase uses deterministic in-memory test doubles; it does not claim a live Firestore or AI-provider integration.

## Request flow

1. Next.js submits `POST /reviews/{review_id}/revisions` with `idempotency_key` and optional `additional_instructions`.
2. FastAPI obtains `creator_id` from the configured authentication dependency. The client cannot supply that identity in the JSON body.
3. `RevisionWorkflowService` reserves `(source_review_id, idempotency_key)`.
4. `RevisionSourceStore` loads the exact review and the exact execution under review, including the original input, output, and reviewer feedback. The host adapter is responsible for resource authorization.
5. The `RevisionExecutionPort` delegates to the normal Runtime execution lifecycle. It must create a new Execution ID and preserve the original execution.
6. A `RevisionReviewCreator` creates a new `PENDING` review for the new execution.
7. `RevisionRecordStore` marks the idempotency reservation complete and stores the resulting execution/review IDs.
8. FastAPI returns the new execution and review IDs. A repeated completed request replays the same result without executing again.

## Test implementation

`tests/integration/test_revision_workflow_e2e.py` composes:

- the real FastAPI revision service router;
- the real `RevisionWorkflowService`;
- the real `CallbackRevisionExecutionPort` bridge;
- in-memory source, reservation, execution, and review test doubles.

The fake execution path deliberately does not call Google ADK or another provider. It simulates the contract of the existing Runtime execution lifecycle and lets tests verify orchestration and duplicate prevention deterministically.

## Invariants tested

- A successful revision creates a new Execution ID and a new `PENDING` Review.
- The original review and execution identifiers remain the source lineage.
- Repeating the same idempotency key returns the same result and does not execute twice.
- A review not in `CHANGES_REQUESTED` cannot be revised.
- Missing source review returns 404 and releases a reservation before execution begins.
- An uncertain execution failure retains the reservation; a subsequent attempt receives a conflict instead of blindly invoking the provider again.
- Creator identity comes from authentication, not request JSON.

## Important limits

- In-memory test doubles are not proof of Firestore transaction correctness or multi-process concurrency behavior.
- `FirestoreRevisionRecordStore`, `FirestoreRevisionSourceStore`, `FirestoreReviewStore`, and `FirestoreWorkflowStore` still require Firestore Emulator or a real test project for integration validation.
- The host must implement resource/tenant authorization and an execution-input loader for the exact execution.
- The host's execution callback must use the existing Runtime lifecycle and provider idempotency support where available. Novacore cannot guarantee exactly-once provider execution or billing.
- A reservation left after an uncertain execution must be reconciled by an operator or a future recovery workflow; it must not be automatically expired.

