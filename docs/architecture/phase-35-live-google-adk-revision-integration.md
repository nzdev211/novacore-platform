# Phase 35 — Live Google ADK Revision Integration

## Goal

Validate the real revision path using a live Google ADK agent and a Firestore
Emulator, without changing the Kernel or Runtime port contracts.

## End-to-end path

1. FastAPI receives an authenticated revision request.
2. `RevisionWorkflowService` reserves the `(source_review_id, idempotency_key)`.
3. `FirestoreRevisionSourceStore` authorizes the creator and loads the exact
   reviewed Execution, its Assignment/Worker reference, persisted output, and
   host-supplied original input.
4. `AgentRevisionExecutionPort` creates a new caller-ID'd Kernel `Execution`,
   persists PENDING then RUNNING, and calls the `AgentExecutor` port.
5. `GoogleADKAgentExecutor` invokes a real ADK `Agent` through `Runner.run_async`.
6. Runtime persists SUCCEEDED and the returned text/metadata.
7. `StoreRevisionReviewCreator` creates a new PENDING review.
8. A repeated request with the same key replays the same Execution and Review.

## Test boundary

`tests/integration/test_revision_workflow_live_adk_firestore.py` is an opt-in
integration test. It requires all of:

- `NOVACORE_RUN_LIVE_ADK_TESTS=1`
- `GOOGLE_API_KEY` for a real Gemini API request
- `FIRESTORE_EMULATOR_HOST` for real Firestore Emulator persistence
- `GOOGLE_CLOUD_PROJECT` (optional; defaults to `novacore-phase35-emulator`)
- `NOVACORE_ADK_MODEL` (optional; defaults to `gemini-2.5-flash`)

The test uses a unique ADK app/session and unique Firestore record IDs per run.
It seeds a source workflow and a CHANGES_REQUESTED review, invokes the real
revision API, checks the persisted SUCCEEDED Execution and new PENDING review,
and confirms same-key replay does not create another execution.

## Architecture constraints

- Kernel unchanged; no new domain types.
- Runtime remains provider-neutral and imports no Google SDK.
- Google ADK remains an adapter behind `AgentExecutor`.
- Host application supplies identity generation and resource authorization.
- Firestore WorkflowStore and ReviewStore remain separate from ADK session storage.
- The live test uses ADK in-memory sessions to isolate the test's concern:
  provider execution plus Novacore Firestore workflow/review persistence.
- A real Gemini request can incur provider charges. The explicit opt-in flag is
  mandatory; ordinary test runs skip this test.

## What this does not prove

It does not validate production IAM, deployed secrets, tenant authorization,
production Firestore contention, or ADK FirestoreSessionService. Those require
separate deployment-level checks.

