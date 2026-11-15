# Phase 33 — Firestore Emulator Revision Validation

## Goal

Validate the Phase 29–30 Firestore revision adapters against the Firestore Emulator without changing the Novacore Kernel or Runtime architecture.

## Covered behavior

- Concurrent callers attempting to reserve the same `(source_review_id, idempotency_key)` result in exactly one reservation owner.
- Other concurrent callers receive `RevisionReservationConflict` and cannot start a duplicate revision.
- Completing a reservation stores the resulting execution and review IDs; reserving the same completed key returns the stored result for replay.
- `FirestoreRevisionSourceStore` loads the exact execution referenced by the source review, verifies that its assignment belongs to the same Work, loads persisted execution output, and calls the host-provided execution-input loader.
- Authorization is delegated to the host callback; unauthorized callers receive no source record.
- `StoreRevisionReviewCreator` persists a new review in `PENDING` state against the newly created execution.

## Test boundary

These tests exercise the Firestore adapters and existing Firestore workflow/review stores. They do not invoke Google ADK or an AI provider. The execution-input loader and authorization callback remain host responsibilities. A successful Emulator run is not a production Firestore deployment certification.

## Architecture constraints preserved

- Kernel domain types are unchanged.
- Runtime remains provider- and infrastructure-independent.
- Firestore remains an adapter package.
- No automatic expiration or blind release of uncertain revision reservations is introduced.
- Exactly-once external provider execution is not guaranteed by Firestore idempotency reservation alone.

