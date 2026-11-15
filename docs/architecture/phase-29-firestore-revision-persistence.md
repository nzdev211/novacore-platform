# Phase 29 — Firestore Revision Persistence

## Goal

Persist the reservation and completed result used by the Phase 28
`RevisionWorkflowService`, using Firestore transactions so concurrent requests
cannot both claim the same `(source_review_id, idempotency_key)` pair.

## New adapter

`FirestoreRevisionRecordStore` implements the Runtime `RevisionRecordStore`
protocol. It writes to the `revision_attempts` collection. Each document stores:

- source review ID and idempotency key;
- state (`reserved` or `completed`);
- when the reservation was created/updated;
- after completion: Activity, Work, new Execution, new Review IDs, and review status.

The document key is a URL-safe Base64 encoding of the source review ID and
idempotency key, separated by a null byte. User-provided values are not used as
raw Firestore path segments.

## Transaction behavior

1. `reserve_revision` creates a `reserved` record if no record exists.
2. A second request for a reserved key receives `RevisionReservationConflict`.
3. A request for a completed key receives the persisted result, which the
   Runtime service can return as an idempotent replay.
4. `complete_revision` changes a reservation to `completed` transactionally.
5. `release_revision` deletes only a still-reserved record. It never deletes a
   completed result.

## Deliberate boundary

This adapter persists the revision idempotency/lineage record only. It does not
load the source review or execution, create an execution, or create a pending
review. Those remain the responsibilities of the Phase 28 ports and their
host-provided adapters. Existing `FirestoreReviewStore` and
`FirestoreWorkflowStore` remain separate.

## Recovery and delivery semantics

A reservation is not automatically expired. If the process crashes after the
provider execution starts but before the result is completed, the reservation
remains and blocks a duplicate request. An operator or recovery workflow must
inspect the execution lifecycle and reconcile the attempt before releasing it.

This prevents duplicate Novacore claims for the same key, but it does not
provide exactly-once provider execution or guarantee that a provider will not
charge twice. Provider-side idempotency support is still required for that.

## Not included

- Firestore-backed source-review authorization/query adapter;
- automatic stale-reservation recovery or lease expiry;
- atomic transaction spanning Firestore revision record, execution lifecycle,
  and human review creation;
- live Firestore Emulator or production integration testing.

