# Phase 26 — Revision and Re-execution Workflow

## Goal

Allow an authorized creator to turn a `CHANGES_REQUESTED` review into a new execution and a new pending review, while preserving the original execution, output, assets, review, and feedback.

## Boundary decisions

- No Kernel changes and no new Kernel domain attributes.
- A revision is a new Runtime execution, not an update to an old Execution.
- Every revised output receives a new ReviewRecord.
- The source review remains terminal with `CHANGES_REQUESTED`.
- The host application owns creator authorization and verifies that the source review is `CHANGES_REQUESTED`.
- Runtime execution lifecycle and idempotency rules from Phases 20–21 remain authoritative.
- Asset references are resolved for the new execution through the Phase 25 review-context resolver; old asset references are not overwritten.

## API contract

`POST /reviews/{review_id}/revisions`

Request:

```json
{
  "additional_instructions": "Use a lower camera angle",
  "idempotency_key": "revision-attempt-001"
}
```

`additional_instructions` is optional. `idempotency_key` is required. The authenticated creator identity is injected by `authenticate_creator`; it is never accepted from request JSON.

Accepted response (`202`):

```json
{
  "source_review_id": "review-1",
  "activity_id": "activity-1",
  "work_id": "work-1",
  "execution_id": "execution-2",
  "review_id": "review-2",
  "status": "PENDING"
}
```

The route is provided by `create_revision_router(create_revision, authenticate_creator)`. The callback is host-owned and receives `source_review_id`, authenticated `creator_id`, `additional_instructions`, and `idempotency_key`.

## Host callback responsibilities

1. Load the source review and enforce tenant/resource authorization for the authenticated creator.
2. Require source review status `CHANGES_REQUESTED`. Reject `PENDING`, `APPROVED`, and `REJECTED` reviews.
3. Resolve the exact source execution and its Activity/Work; do not select an arbitrary latest execution.
4. Build the next agent request from the original brief, source execution output, source review feedback, and optional additional instructions.
5. Create a new Execution identity and pass the idempotency key through the Runtime execution path. Never reuse the source ExecutionId.
6. Persist the new execution lifecycle using the Phase 20–21 rules. Do not automatically retry an uncertain `RUNNING` execution.
7. After successful generation, create a new `PENDING` review referencing the new execution and the same Activity/Work.
8. Return the new execution and review identifiers in the response contract.

The callback must be idempotent: repeating the same key for the same source review must return the same revision result rather than create another execution. Reusing the key for a different source review must be rejected. A new deliberate attempt requires a new key.

## Failure and recovery

- If the source review is not `CHANGES_REQUESTED`, no new execution is created.
- If generation fails, persist the failure using the existing execution lifecycle. Do not create a pending review for failed output.
- If the process stops after generation succeeds but before review creation, recovery must detect the successful execution and finish review creation without invoking the model again.
- A duplicate HTTP request with the same idempotency key must not trigger duplicate provider work.
- Exactly-once provider execution is not guaranteed unless the provider supports idempotency; Phase 21's limitations still apply.

## History model

Example:

```text
Activity A
└── Work W
    ├── Execution 1 → Review 1 (CHANGES_REQUESTED)
    └── Execution 2 → Review 2 (PENDING)
```

The original review and execution remain readable. The new review's Phase 25 context resolver must return assets and shot specification from Execution 2, not Execution 1.

## Out of scope

- Kernel schema changes.
- Automatic approval or Activity completion.
- A full creator-facing revision UI.
- Asset upload/versioning implementation.
- Automatic retry of uncertain executions.
- Provider-level exactly-once guarantees.

