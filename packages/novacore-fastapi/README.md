# novacore-fastapi

FastAPI inbound adapter for Novacore Platform.

## Human review routes (Phase 23)

The package exposes `create_human_review_router`, which wires the Phase 22
Runtime `HumanReviewService` and `ReviewStore` into authenticated HTTP routes.

Install:

```bash
pip install 'novacore-fastapi[fastapi]'
```

Example composition:

```python
from fastapi import FastAPI, Depends
from novacore.fastapi import create_human_review_router
from novacore.runtime.services import HumanReviewService
from novacore.firestore import FirestoreReviewStore

review_store = FirestoreReviewStore()
review_service = HumanReviewService(review_store)

def current_user_id():
    # Replace with your authentication provider integration.
    # Must return the authenticated user's stable ID.
    ...

app = FastAPI()
app.include_router(
    create_human_review_router(
        review_service=review_service,
        review_store=review_store,
        authenticate_reviewer=current_user_id,
    )
)
```

### Routes

| Method | Route | Purpose |
|---|---|---|
| POST | `/reviews` | Create a pending review |
| GET | `/reviews/{review_id}` | Retrieve review state |
| POST | `/reviews/{review_id}/decision` | Approve, request changes, or reject |

All routes require the injected authentication dependency. Reviewer identity is
derived from that dependency, never from the request body.

The application remains responsible for authorization (for example, whether
the authenticated reviewer may review a particular Activity). This adapter
does not provide authentication, role management, CSRF protection, or tenant
isolation. Add those policies in the composition/application layer before
exposing these endpoints publicly.

Review decisions do not automatically launch another model execution or mark
the Activity complete.

