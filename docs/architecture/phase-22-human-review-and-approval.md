# Phase 22 — Human Review and Approval

## Goal

Persist a human decision for generated Creative Studio work so a workflow can
pause for review and later reopen the review state.

## Scope

- Add Runtime-owned `ReviewRecord`, `ReviewStatus`, and `ReviewStore` contracts.
- Add a Runtime `HumanReviewService` for submission and decision recording.
- Add `FirestoreReviewStore` using transactional create and compare-and-set updates.
- Keep review state outside the Kernel; no new Kernel entity or ID type is introduced.

## Review states

- `PENDING`: awaiting a human decision.
- `APPROVED`: accepted.
- `CHANGES_REQUESTED`: requires a new generation/revision workflow.
- `REJECTED`: not accepted.

A decision is terminal for that review record. A revision creates a new review
record linked to the new ExecutionId; the previous decision remains auditable.

## Boundaries

- Runtime owns review workflow policy.
- Firestore persists review records.
- The UI/authentication layer supplies reviewer identity; this phase does not
  authenticate reviewers or define permissions.
- The review record references ActivityId, WorkId, and ExecutionId. The generated
  artifact itself remains in external asset storage and is not copied into Firestore.
- Approval does not automatically mark Activity or Work complete.
- A requested change does not automatically trigger another model call.

