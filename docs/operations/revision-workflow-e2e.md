# Operating the End-to-End Revision Workflow

## API

`POST /reviews/{review_id}/revisions`

Example request:

```json
{
  "additional_instructions": "Slow the camera movement and preserve the character's appearance.",
  "idempotency_key": "client-generated-stable-key"
}
```

The authenticated creator identity is injected by FastAPI. Do not add `creator_id` to the request body.

## Response

A successful request returns HTTP `202` with `source_review_id`, `activity_id`, `work_id`, `execution_id`, `review_id`, `status`, and `replayed`. A replay returns the same result with `replayed: true`.

## Failure handling

- `403`: caller is authenticated but not authorized by the host's authorization policy.
- `404`: source review does not exist or is intentionally hidden from the caller.
- `409`: source review is not `CHANGES_REQUESTED`, the key is already in progress, or the key conflicts with an existing result.
- `422`: malformed request.
- `503`: persistence or execution outcome requires investigation. Check the revision reservation and execution lifecycle before retrying.

Do not release a reservation after an execution may have started. First inspect the corresponding Execution lifecycle record and provider-side idempotency evidence.

## Test command

From the repository root, with package `src` directories on `PYTHONPATH`:

```bash
pytest -q tests/integration/test_revision_workflow_e2e.py
```

This test uses in-memory fakes and does not need Firestore credentials or an AI provider.

