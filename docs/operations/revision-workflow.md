# Revision Workflow Operations

## Register the router

```python
from novacore.fastapi import create_revision_router

app.include_router(create_revision_router(
    create_revision=create_revision,
    authenticate_creator=authenticate_creator,
))
```

The `create_revision` callback is application-owned:

```python
def create_revision(*, source_review_id: str, creator_id: str,
                    additional_instructions: str | None,
                    idempotency_key: str) -> dict | None:
    ...
```

It must authorize the creator, require `CHANGES_REQUESTED`, reuse the original Activity and Work, create a distinct Execution, and create a new pending review only after successful generation. It must be idempotent for a given source review and idempotency key.

## Suggested request

```bash
curl -X POST "$NOVACORE_API_URL/reviews/review-1/revisions" \
  -H "Authorization: Bearer $CREATOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"additional_instructions":"Use a lower camera angle","idempotency_key":"revision-attempt-001"}'
```

Do not trust a creator ID from the request body. The authentication dependency supplies it. The host must also perform resource-level authorization; authentication alone is not enough.

## Operational checks

- Confirm the source review is `CHANGES_REQUESTED` before starting work.
- Trace source review ID, new execution ID, and new review ID together.
- Use the same idempotency key when retrying an HTTP request whose response was lost.
- Inspect execution lifecycle before any manual retry. `RUNNING` may have an uncertain provider outcome.
- Verify the new review context resolves the new execution's output and asset URLs.

## Security note

The route's authentication dependency identifies the creator, but the callback must still authorize that creator against the specific review and tenant. Do not expose the endpoint based on authentication alone.

