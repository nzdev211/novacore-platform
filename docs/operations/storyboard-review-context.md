# Storyboard Review Context Operations

## Install and register

Install the FastAPI extra, then register the optional router alongside the Phase 23 review router:

```python
from novacore.fastapi import create_review_context_router

app.include_router(create_review_context_router(
    load_review_context=load_review_context,
    authenticate_reviewer=authenticate_reviewer,
))
```

`load_review_context` must be an application-owned resolver with signature:

```python
def load_review_context(*, review_id: str, reviewer_id: str) -> dict | None:
    ...
```

The resolver must:
1. Load the review.
2. Enforce tenant and resource-level authorization for the authenticated reviewer.
3. Load the matching workflow snapshot/execution.
4. Verify the execution ID belongs to the review.
5. Map the actual worker output to `brief`, `shot_spec`, and `assets`.
6. Return short-lived signed asset URLs or protected URLs.

Do not accept `reviewer_id` from browser request data. It is supplied by the authentication dependency.

## Next.js configuration

Set `NEXT_PUBLIC_NOVACORE_API_URL` to the FastAPI service origin. Ensure API CORS permits the web origin, or use a same-origin reverse proxy. Set a Content Security Policy that permits the required API and asset hosts for `connect-src`, `img-src`, and `media-src`.

## Endpoint

`GET /reviews/{review_id}/context`

Returns a review context object with a flexible shot specification and asset references. The UI treats this endpoint as optional: if it is not registered or returns an error, the review decision workflow remains available but the preview section shows an unavailable message.

## Security and privacy

Signed URLs should have short expiry times. Avoid logging signed URLs. Do not expose storage credentials or private storage paths. The resolver must authorize access to both the review and every asset referenced by it.

