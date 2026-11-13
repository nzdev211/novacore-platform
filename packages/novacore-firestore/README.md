# novacore-firestore

Firestore persistence adapter for Novacore Runtime.

## Implemented

- `FirestoreWorkflowStore` implements Runtime's `WorkflowStore` protocol.
- Initial Request, Context, Objective, Activity, Planning, Work, Contract(s), and Assignment records are committed in one Firestore transaction.
- Kernel Execution identities and Runtime lifecycle records are persisted separately.
- Lifecycle transitions use Firestore transactions with expected-status checks.
- Execution status, output, metadata, and error details can be loaded for recovery inspection.
- Non-null idempotency keys are reserved transactionally when an execution is claimed as `running`; a different ExecutionId cannot reserve the same key.
- Domain identifiers are encoded as URL-safe Base64 document IDs, so arbitrary identifier values do not become Firestore path separators.
- SDK import and client construction are lazy; the base package can be imported without installing the Google Cloud SDK.

## Install

Install the Kernel and Runtime packages in the same environment, then:

```bash
pip install -e 'packages/novacore-firestore[firestore]'
```

## Configure

The default constructor uses Google Cloud Application Default Credentials:

```python
from novacore.firestore import FirestoreWorkflowStore

store = FirestoreWorkflowStore()
```

Or inject an already configured Firestore client:

```python
store = FirestoreWorkflowStore(client=firestore_client)
```

Set up credentials outside source control. Never commit API keys or service account files.

## Collections

`requests`, `contexts`, `objectives`, `activities`, `plannings`, `works`, `contracts`, `assignments`, `executions`, and `execution_lifecycle`.

References are stored as their domain identifier values. Context metadata is converted recursively to Firestore-native maps and arrays. Python tuples and sets are stored as arrays; Firestore does not preserve those collection types.

## Atomicity and consistency

The initial workflow records are written in one Firestore transaction. Execution lifecycle transitions and idempotency reservations use separate transactions. Each lifecycle transition checks the expected prior status. The adapter does not keep a transaction open while an external agent runs.

The adapter supports workflow and lifecycle reads needed for inspection and resume. It does not implement deletes, worker directory storage, ADK session persistence, automatic retries, leases, or exactly-once provider execution. The idempotency reservation provides at-most-one Novacore claim per key, not provider-side deduplication.

## Testing

The adapter tests use a fake Firestore client and transaction decorator. They verify document mapping, atomic transaction grouping, safe document IDs, lifecycle transitions, idempotency reservation, and persistence error translation without requiring a Google Cloud project.

