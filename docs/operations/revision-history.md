# Revision History Integration

## Register the router

```python
from novacore.fastapi import create_revision_history_router

app.include_router(
    create_revision_history_router(
        load_revision_history=load_history_for_authorized_reviewer,
        authenticate_reviewer=get_authenticated_reviewer_id,
    )
)
```

The example callback names are application-owned functions. Implement them using the application's actual review and execution persistence APIs; do not copy guessed repository methods.

## Callback contract

`load_revision_history(review_id: str, reviewer_id: str) -> dict | None`

Return a response with `activity_id`, `work_id`, and an `entries` list ordered oldest-first. Every entry must include `review_id`, `execution_id`, `activity_id`, `work_id`, `review_status`, and ISO-8601 `created_at`. Optional fields are `execution_status`, `source_review_id`, and `feedback`.

Before returning data:

1. Authenticate the reviewer and authorize access to the requested review.
2. Resolve the persisted revision lineage, using the source-review relationship captured when Phase 26 creates a revision.
3. Verify all reviews and executions belong to the same Activity and Work.
4. Verify each execution is the exact execution referenced by its review.
5. Detect cycles, missing records, duplicate IDs, and invalid parent relationships.
6. Return oldest-first; do not infer lineage by sorting timestamps or choosing the latest execution alone.
7. Do not return asset URLs or secrets. The Phase 25 context endpoint remains responsible for protected asset references.

Return `None` for an unknown or inaccessible review if the application intentionally conceals resource existence. Raise `PermissionError` for a known authorization denial if the application distinguishes it.

## Frontend

The review page calls `GET /reviews/{review_id}/history`. Configure `NEXT_PUBLIC_NOVACORE_API_URL` as in Phase 24. History is an independent panel; a history failure does not disable review decisions.

## Security

The API's injected reviewer identity must come from the trusted authentication layer, never request JSON. The callback must enforce tenant and resource-level authorization for every item in the chain. Do not expose other users' reviews merely because they share an Activity or Work.

