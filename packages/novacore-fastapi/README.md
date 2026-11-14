# novacore-fastapi — Phase 26 addition

Phase 26 adds an optional authenticated revision endpoint alongside the Phase 23 review routes and Phase 25 review-context route.

## Revision route

```python
from novacore.fastapi import create_revision_router

app.include_router(create_revision_router(
    create_revision=create_revision,
    authenticate_creator=authenticate_creator,
))
```

The host application supplies both callbacks. `authenticate_creator` returns the authenticated creator's stable ID. `create_revision` performs resource authorization, requires the source review to be `CHANGES_REQUESTED`, orchestrates a new Runtime execution, and creates a new pending review after successful generation.

`POST /reviews/{review_id}/revisions`

Request body:

```json
{
  "additional_instructions": "Use a lower camera angle",
  "idempotency_key": "revision-attempt-001"
}
```

The idempotency key is required. The authenticated creator ID is injected and cannot be supplied in the body. The callback must return the same revision result when the same key is repeated for the same source review.

The route does not implement provider execution, persistence, tenant authorization, or identity integration. See `docs/operations/revision-workflow.md` for callback requirements and recovery behavior.

