# Execution Lifecycle Operations

The Firestore adapter stores Runtime execution lifecycle documents in the `execution_lifecycle` collection, separate from Kernel `executions` records and Google ADK session documents.

Statuses are `pending`, `running`, `succeeded`, and `failed`. The Runtime uses transactional expected-status transitions. A conflict indicates that another caller or process already changed the state; do not force-overwrite it.

A `running` record after a crash is an uncertain outcome, not proof that the provider did no work. Use `ExecutionRecoveryService.inspect(execution_id)` and reconcile the provider/ADK execution context before taking manual recovery action.

Phase 21 adds Firestore idempotency-key reservation. It prevents a different Novacore ExecutionId from claiming the same non-null key. It does not guarantee exactly-once provider execution or billing. Automatic retries, lease expiry, heartbeat, cancellation, timeout, and stale-running takeover remain out of scope.

