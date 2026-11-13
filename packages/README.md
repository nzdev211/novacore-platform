# Novacore Platform — Phase 21

Phase 21 is the latest implementation snapshot in this series. It builds on workflow retrieval (Phase 19) and Runtime-owned execution lifecycle persistence (Phase 20) with conservative recovery classification and Firestore-backed idempotency-key reservation.

## Execution recovery and idempotency

- Runtime classifies persisted executions as safe to start, already succeeded, outcome uncertain, or requiring manual review.
- Firestore reserves a non-null idempotency key transactionally so a different ExecutionId cannot claim the same key.
- Interrupted `RUNNING` executions are outcome-uncertain and must be reconciled before another generation is approved.
- Provider-side exactly-once execution or billing is **not** guaranteed by the Firestore reservation. It requires explicit provider/adapter support.

See `docs/architecture/phase-21-execution-recovery-idempotency.md`, `docs/operations/execution-recovery-idempotency.md`, and `PHASE21_TEST_RESULTS.txt`.

The snapshot is a source archive, not a GitHub commit or push.

