# Phase 20 — Execution Lifecycle and Recovery

## Decision

Execution lifecycle is Runtime-owned metadata. The Kernel `Execution` remains an
immutable identity/reference record and is not expanded with provider status,
output, retry counters, or timestamps.

## Lifecycle

`pending -> running -> succeeded | failed`

- `pending` is persisted before an external worker is invoked.
- `running` is acquired with a compare-and-set transition from `pending`.
- A successful result and metadata are persisted as `succeeded`.
- An exception is persisted as `failed`, then propagated to the caller.
- Firestore transitions are transactional compare-and-set operations. A stale
  caller cannot transition an execution from an unexpected state.

## Recovery boundary

This phase records enough state to inspect an interrupted execution and prevents
reusing the same execution identity through the normal `pending -> running`
claim. It does not automatically retry a `running` execution: after a process
crash, the external provider may have completed even if Novacore did not receive
its response. Retrying safely requires provider idempotency keys or a durable
reconciliation strategy and is intentionally deferred.

## Separation

- Kernel: `Execution` identity and `AssignmentId` only.
- Runtime: `ExecutionStatus`, `ExecutionRecord`, state transitions and policy.
- Firestore: durable compare-and-set persistence.
- Google ADK: internal agent/session execution remains separate.

## Limitations

No automatic retry, lease expiry, heartbeat, cancellation, timeout, attempt
number, or cross-provider exactly-once guarantee is introduced.


## Subsequent phase clarification

Phase 21 adds recovery inspection and idempotency-key reservation on top of this
lifecycle. It does not change the Phase 20 state model or make retries automatic.
A `running` execution is still outcome-uncertain after a crash. Reservation
prevents duplicate Novacore claims for a key; exactly-once provider execution
requires explicit provider-side idempotency support and reconciliation. See
`phase-21-execution-recovery-idempotency.md`.

