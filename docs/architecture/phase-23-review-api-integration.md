# Phase 23 — Creative Studio Review API Integration

## Objective

Expose the Phase 22 Runtime human-review capability through an inbound FastAPI
adapter without moving review policy into HTTP handlers or introducing a
FastAPI dependency into Runtime or Kernel.

## Routes

- `POST /reviews`: create a pending review using caller-supplied review,
  activity, work, and execution identifiers.
- `GET /reviews/{review_id}`: retrieve review state.
- `POST /reviews/{review_id}/decision`: record APPROVED,
  CHANGES_REQUESTED, or REJECTED.

## Security boundary

Each route uses an injected authentication dependency. The decision endpoint
obtains reviewer identity from the authenticated principal; it never accepts
reviewer identity from request JSON.

Authentication and authorization implementation, resource-level access
checks, tenant isolation, and audit export remain responsibilities of the
application composition/security layer.

## Error mapping

- 404: review does not exist.
- 409: review already decided or concurrent decision conflict.
- 422: invalid request or decision.
- 503: persistence unavailable.

## Out of scope

No UI frontend, automatic revision generation, automatic Activity completion,
asset binary delivery, or provider invocation is implemented in this phase.

