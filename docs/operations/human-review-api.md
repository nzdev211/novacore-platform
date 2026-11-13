# Human Review API Operations

## Install

```bash
pip install 'novacore-fastapi[fastapi]'
```

Ensure the application also installs its selected Runtime and persistence
adapters.

## Wire the router

Create one `ReviewStore`, pass it to `HumanReviewService`, and inject both into
`create_human_review_router`. Supply an authentication dependency that returns
the stable ID of the authenticated reviewer.

Do not use a placeholder identity resolver in production.

## Authorization

Authentication alone is not sufficient. Before production exposure, enforce
that the authenticated user may access the target Activity/Work and may make
the requested decision. Add tenant/resource scoping and rate limits as
appropriate to the application.

## Operational behavior

- `POST /reviews` creates a PENDING review.
- `GET /reviews/{review_id}` returns the persisted record.
- `POST /reviews/{review_id}/decision` records one terminal decision.
- Repeated decisions return HTTP 409.
- Missing review IDs return HTTP 404.
- Persistence failures return HTTP 503.

A CHANGES_REQUESTED decision is a recorded instruction for the workflow
coordinator. It does not itself regenerate content. The coordinator should
create a new execution/review cycle after applying Phase 20–21 recovery and
idempotency checks.

