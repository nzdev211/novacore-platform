# Phase 31 — FastAPI Revision Endpoint Integration

## Goal

Connect the existing FastAPI revision endpoint directly to `RevisionWorkflowService`, while retaining the callback-based router for hosts that need a custom integration.

## Changes

- Add `create_revision_service_router(revision_service, authenticate_creator)`.
- Export the new factory from `novacore.fastapi`.
- Keep `POST /reviews/{review_id}/revisions` and the existing request contract.
- Include `replayed` in the response so clients can distinguish a newly completed request from an idempotent replay.
- Convert the Runtime `RevisionResult` dataclass to the API response model.
- Map authorization, review eligibility, idempotency conflicts, validation, and workflow failures to HTTP status codes.
- Introduce `RevisionInProgressError` in the Runtime revision port contract. The Firestore reservation conflict now derives from this Runtime-level error, allowing the API to return HTTP 409 without importing Firestore into FastAPI.

## HTTP behavior

| Condition | HTTP status |
|---|---:|
| Revision completed or completed result replayed | 202 |
| Source review missing | 404 |
| Creator not authorized | 403 |
| Source review is not `CHANGES_REQUESTED` | 409 |
| Idempotency key already reserved or conflicts | 409 |
| Invalid request or service arguments | 422 |
| Persistence or workflow failure | 503 |

A 503 response intentionally tells the client to inspect workflow state before retrying. It must not blindly generate a new idempotency key after an uncertain failure.

## Application wiring

The host application constructs the Runtime service with its existing adapters, then injects that service into the FastAPI router:

```python
from fastapi import FastAPI
from novacore.fastapi import create_revision_service_router

app = FastAPI()

revision_service = build_revision_workflow_service(
    source_store=revision_source_store,
    execution_port=revision_execution_port,
    revision_store=revision_record_store,
    review_creator=revision_review_creator,
)

app.include_router(
    create_revision_service_router(
        revision_service=revision_service,
        authenticate_creator=authenticate_creator,
    )
)
```

`build_revision_workflow_service`, the adapter instances, and `authenticate_creator` are host-application composition responsibilities; they are not functions provided by this patch.

## Boundaries

- FastAPI does not import Google ADK or call a model provider.
- Runtime owns revision orchestration.
- Firestore owns persistence and atomic reservation.
- The host owns authentication and resource-level authorization.
- Kernel schemas remain unchanged.
- Existing callback-based `create_revision_router` remains available for backward compatibility.

## Not included

- Automatic recovery of a reserved attempt after a process crash.
- Provider-level exactly-once execution or billing guarantees.
- A production identity provider or tenant authorization implementation.
- A runnable host application's complete dependency-injection/composition root.
- Live Firestore or provider integration.

