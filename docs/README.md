# Novacore Platform — Phase 20

Phase 19 adds read-side workflow persistence so Creative Studio can reopen a saved workflow. See:

- `docs/architecture/phase-19-workflow-retrieval-and-resume.md`
- `docs/operations/workflow-retrieval-and-resume.md`
- `PHASE19_TEST_RESULTS.txt`

The snapshot includes the Phase 18 platform baseline plus Phase 19 changes. It is a source archive, not a GitHub commit or push.

## Scope boundary

Workflow retrieval restores business records. It does not automatically retry or resume an interrupted provider call. ADK session restoration remains a separate responsibility handled by the configured Google ADK SessionService.


## Latest implementation snapshot — Phase 20

Phase 20 adds Runtime-owned execution lifecycle metadata and Firestore
compare-and-set transitions (`pending`, `running`, `succeeded`, `failed`). The
Kernel `Execution` model remains unchanged. See
`docs/architecture/phase-20-execution-lifecycle-and-recovery.md` and
`docs/operations/execution-lifecycle.md`. Automatic retries and crash
reconciliation are intentionally not implemented.


## Subsequent recovery capability — Phase 21

Phase 21 builds on the lifecycle records introduced in Phase 20. It adds
conservative recovery inspection and idempotency-key reservation. A persisted
`running` execution remains outcome-uncertain until reconciled; idempotency
reservation prevents duplicate Novacore claims but does not guarantee exactly-once
execution or billing by an external provider. See
`docs/architecture/phase-21-execution-recovery-idempotency.md` and
`docs/operations/execution-recovery-idempotency.md`.

