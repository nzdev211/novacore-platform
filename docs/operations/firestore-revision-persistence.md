# Firestore Revision Persistence — Operations

## Install

```bash
pip install -e 'packages/novacore-firestore[firestore]'
```

## Configure

```python
from novacore.firestore import FirestoreRevisionRecordStore

revision_store = FirestoreRevisionRecordStore()  # Application Default Credentials
# Or inject an already configured google.cloud.firestore.Client.
```

Pass `revision_store` to the Phase 28 `RevisionWorkflowService` as its
`revision_store` dependency.

## Collections

The adapter uses `revision_attempts`. It does not replace `human_reviews`,
`executions`, or `execution_lifecycle`.

## Operational rule

Do not manually delete a `reserved` record just because it is old. First inspect
the corresponding execution lifecycle. A provider call may have completed even
if the application failed before recording the revision result. Releasing that
reservation without reconciliation can cause a second provider call.

Completed records are retained for idempotent replay and revision history.
Back up and protect this collection with the same access controls as workflow
and review records.

