# novacore-firestore

Firestore persistence adapter for Novacore Runtime.

## Implemented

- `FirestoreWorkflowStore` implements Runtime's `WorkflowStore` protocol.
- Initial Request, Context, Objective, Activity, Planning, Work, Contract(s),
  and Assignment records are committed in one Firestore transaction.
- Kernel Execution identities and Runtime lifecycle records are persisted separately.
- Lifecycle transitions use Firestore transactions with expected-status checks.
- Execution status, output, metadata, and error details can be loaded for recovery inspection.
- Domain identifiers are encoded as URL-safe Base64 document IDs, so arbitrary
  identifier values do not become Firestore path separators.
- SDK import and client construction are lazy; the base package can be imported
  without installing the Google Cloud SDK.

## Install

Install the Kernel and Runtime packages in the same environment, then:

```bash
pip install -e 'packages/novacore-firestore[firestore]'
```

## Configure

The default constructor uses Google Cloud Application Default Credentials:

```python
from novacore.firestore import FirestoreWorkflowStore

store = FirestoreWorkflowStore()
```

Or inject an already configured Firestore client:

```python
store = FirestoreWorkflowStore(client=firestore_client)
```

Set up credentials outside source control. Never commit API keys or service
account files.

## Collections

`requests`, `contexts`, `objectives`, `activities`, `plannings`, `works`,
`contracts`, `assignments`, `executions`, and `execution_lifecycle`.

References are stored as their domain identifier values. Context metadata is
converted recursively to Firestore-native maps and arrays. Python tuples and
sets are stored as arrays; Firestore does not preserve those collection types.

## Atomicity and consistency

The initial workflow records are written in one Firestore transaction.
Execution lifecycle transitions are separate transactions and occur before,
during, and after agent execution. Each transition checks the expected prior
status. The adapter does not keep a transaction open while an external agent
runs.

The adapter supports workflow and lifecycle reads needed for inspection and
resume. It does not implement deletes, worker directory storage, ADK session
persistence, automatic retries, leases, or exactly-once provider execution.

## Testing

The adapter tests use a fake Firestore client and transaction decorator. They
verify document mapping, atomic transaction grouping, safe document IDs, and
persistence error translation without requiring a Google Cloud project.


## Human review persistence (Phase 22)

`FirestoreReviewStore` persists Runtime-owned review records in the
`human_reviews` collection. It uses transactional creation and status-checked
updates. Reviewer authentication and authorization remain responsibilities
of the calling application.

## Revision persistence (Phase 29)

`FirestoreRevisionRecordStore` implements the Runtime `RevisionRecordStore`
port. It stores reservation and completed-result records in `revision_attempts`
so a repeated `(source_review_id, idempotency_key)` can be rejected while
in-progress or safely replayed after completion.

```python
from novacore.firestore import FirestoreRevisionRecordStore

revision_store = FirestoreRevisionRecordStore()
```

Unfinished reservations are not automatically expired. Inspect the linked
execution lifecycle before releasing one; the external provider may already
have completed the call.


## Revision integration (Phase 30)

- `FirestoreRevisionSourceStore` resolves a review to its exact Execution and lifecycle output, with required host authorization and original-input loader callbacks.
- `StoreRevisionReviewCreator` creates the next `PENDING` review through the existing `ReviewStore` port.
- `FirestoreRevisionRecordStore` (Phase 29) stores atomic revision reservations and completed revision links.

The execution adapter is `CallbackRevisionExecutionPort` in `novacore-runtime`. Its host callback must use the existing Runtime execution lifecycle; the Firestore package does not invoke agent providers directly.

See `docs/architecture/phase-30-revision-source-and-execution-integration.md` and `docs/operations/revision-integration.md` for required host wiring and security boundaries.


# Novacore Phase 33 — Firestore Emulator Revision Validation

Phase 33 adds opt-in integration coverage for the existing Firestore revision adapters.

## What changed

- Added `tests/integration/test_revision_firestore_emulator.py` under `packages/novacore-firestore`.
- Exported the existing revision adapters from `novacore.firestore` for a consistent public package surface.
- Added architecture and operations documentation for the Emulator test boundary and run commands.

## What the tests cover

1. Concurrent attempts to reserve one revision idempotency key.
2. Safe replay after a revision reservation has been completed.
3. Loading the exact source review and execution from Firestore-backed workflow/review records.
4. Host authorization callback behavior and execution-input loading.
5. Creating and reading the next `PENDING` human review.

## Plain-English explanation

The Emulator is a local Firestore-compatible service. These tests check that the database behavior—not just an in-memory fake—protects a revision from being started twice with the same key. They also check that a revision uses the exact execution that the reviewer commented on, and that the next review is saved as waiting for human approval.

The tests do not generate images or call an AI model. They test persistence and adapter wiring only. Your application still supplies the authorization rules and the original execution input loader.

## Run

See `docs/operations/firestore-emulator-revision-tests.md`.

## Validation in this build environment

- Existing Firestore revision unit/fake-client tests: passed.
- Emulator tests: not executed because `google-cloud-firestore` and `FIRESTORE_EMULATOR_HOST` are not available in this environment.
- Python compilation: passed.

