# Reopen a Creative Studio workflow

`FirestoreWorkflowStore.load_workflow(activity_id)` returns a `WorkflowSnapshot` for an existing Activity, or `None` if no Activity document exists.

```python
from novacore.kernel.identity import ActivityId
from novacore.firestore import FirestoreWorkflowStore

store = FirestoreWorkflowStore()
snapshot = store.load_workflow(ActivityId("activity-identifier"))
if snapshot is None:
    # Show not found / start a new workflow.
    ...
else:
    # Restore the application view from snapshot records.
    # Loading does not execute or retry an agent.
    ...
```

The snapshot contains the Activity's Request, Context, Objective, Planning records, Work records, Contracts, Assignments, and associated Execution identities. The ADK session can be restored separately through the configured ADK SessionService using the same ADK app/user/session identifiers originally supplied by the application.

Do not assume an Execution is safe to retry merely because it is present. Use `ExecutionRecoveryService.inspect(execution_id)` to classify its persisted lifecycle state. A `RUNNING` execution is outcome-uncertain; a `SUCCEEDED` execution should reuse its persisted output; a `FAILED` execution requires review before a new logical generation is approved. See `docs/operations/execution-recovery-idempotency.md`.

