# Firestore WorkflowStore Setup

## Install packages

```bash
pip install -e packages/novacore-kernel
pip install -e packages/novacore-runtime
pip install -e 'packages/novacore-firestore[firestore]'
```

## Configure credentials

Use Google Cloud Application Default Credentials:

```bash
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT="your-project-id"
```

In production, prefer the workload identity or service-account mechanism supported by your deployment platform. Do not commit credentials.

## Instantiate

```python
from novacore.firestore import FirestoreWorkflowStore

workflow_store = FirestoreWorkflowStore()
```

Or inject a configured `google.cloud.firestore.Client`:

```python
workflow_store = FirestoreWorkflowStore(client=firestore_client)
```

## Load a saved workflow

Use the Activity identifier to retrieve the persisted workflow without invoking a worker:

```python
snapshot = workflow_store.load_workflow(activity_id)
if snapshot is None:
    # No Activity with this identifier exists.
    ...
else:
    activity = snapshot.activity
    works = snapshot.works
    executions = snapshot.executions
```

The snapshot also contains `request`, `context`, `objective`, `planning`, `contracts`, and `assignments`. A missing Activity returns `None`. Missing required related records or read errors raise `PersistenceError`; do not interpret those cases as an empty workflow.

The adapter performs multiple reads and queries. If concurrent writers can modify a workflow while it is being loaded, the returned view is not guaranteed to represent one cross-collection transaction snapshot.

## Firestore Emulator

Start the Firestore Emulator using the Google Cloud CLI, then configure:

```bash
export FIRESTORE_EMULATOR_HOST="127.0.0.1:8080"
export GOOGLE_CLOUD_PROJECT="novacore-firestore-test"
```

Install test dependencies and run:

```bash
pip install -e 'packages/novacore-firestore[firestore,test]'
pytest packages/novacore-firestore/tests
```

The emulator integration test is skipped unless `FIRESTORE_EMULATOR_HOST` is present. Unit tests do not require credentials or a running emulator.

## Responsibility boundary

`FirestoreWorkflowStore` persists business workflow records. It does not persist Google ADK session state, choose retry policy, or guarantee exactly-once external provider execution. Use the Google ADK Firestore session integration for ADK sessions and Runtime execution lifecycle services for recovery policy.

