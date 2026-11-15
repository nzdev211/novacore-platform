# Revision Endpoint Integration — Operations

## Route

`POST /reviews/{review_id}/revisions`

Example request:

```http
POST /reviews/review-123/revisions
Content-Type: application/json
Authorization: Bearer <host-issued-token>
```

```json
{
  "idempotency_key": "revision-review-123-v2",
  "additional_instructions": "Keep the character design unchanged and improve the camera movement."
}
```

The authenticated creator ID is injected by the host's `authenticate_creator` dependency. It must never be accepted from the JSON body.

Example successful response:

```json
{
  "source_review_id": "review-123",
  "activity_id": "activity-456",
  "work_id": "work-789",
  "execution_id": "execution-new",
  "review_id": "review-new",
  "status": "PENDING",
  "replayed": false
}
```

If the same completed request is submitted again with the same source review and idempotency key, the response contains the original execution/review IDs and `replayed: true`.

## Host wiring checklist

1. Construct the Phase 28 `RevisionWorkflowService` with the Phase 29 revision record store and Phase 30 source, execution, and review adapters.
2. Inject the service into `create_revision_service_router`.
3. Inject an authentication dependency that returns a stable authenticated creator ID.
4. Ensure the source store performs resource-level authorization for the Activity and Work before returning execution data.
5. Ensure the execution adapter creates a new Execution and uses the normal Runtime lifecycle/idempotency path.
6. Keep the same idempotency key for retries of the same logical request.
7. Treat HTTP 409 as a conflict requiring a new user decision or reconciliation. Treat HTTP 503 as an uncertain state: inspect the revision attempt before retrying.
8. Do not expose signed media URLs or private execution inputs in API logs.

## Security notes

Authentication alone does not establish access to a particular review. The source-store authorization callback must verify that the authenticated creator is allowed to revise the exact review, Activity, and Work. Apply tenant isolation in that callback and in all persistence queries.

## Troubleshooting

- `403`: authenticated creator lacks resource-level permission.
- `404`: source review does not exist or the host intentionally hides unauthorized resource existence.
- `409`: review is not in `CHANGES_REQUESTED`, or the idempotency key is already reserved/conflicting.
- `422`: request payload or required service argument is invalid.
- `503`: persistence or workflow failure. Check `revision_attempts`, Execution lifecycle state, and review records before attempting recovery.

Do not delete a reservation merely because an HTTP request timed out. A provider call may already have started.

