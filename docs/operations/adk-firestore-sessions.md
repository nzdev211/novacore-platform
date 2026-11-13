# Google ADK Firestore Session Setup

## 1. Install

```bash
pip install -e packages/novacore-kernel
pip install -e packages/novacore-runtime
pip install -e 'packages/novacore-google-adk[firestore]'
```

The Firestore extra installs Google ADK 2.14+ (2.x) and
`google-cloud-firestore`.

## 2. Configure Google Cloud credentials

Local development:

```bash
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT="your-project-id"
```

In production, use the deployment platform's workload identity or
Application Default Credentials. Do not commit credentials.

## 3. Configure the executor

```python
executor = GoogleADKAgentExecutor.from_agent(
    agent=agent,
    config=GoogleADKConfig(
        app_name="novacore_creative_studio",
        session_backend="firestore",
        firestore_root_collection="novacore-adk-sessions",
    ),
)
```

The official ADK Firestore service creates a Firestore AsyncClient when one
is not injected. An already-configured `google.cloud.firestore.AsyncClient`
can be passed using `firestore_client=...`.

## 4. Keep the two persistence layers distinct

Configure `FirestoreWorkflowStore` separately for Novacore workflow
records. Do not point both systems at the same collection root.

- WorkflowStore: Request, Context, Objective, Activity, Planning, Work,
  Contract, Assignment, Execution.
- ADK session service: ADK session documents, events, and ADK state.

## 5. Emulator / cloud validation

Use the Firestore Emulator by setting `FIRESTORE_EMULATOR_HOST`, then run
the adapter tests and a real ADK agent invocation. The unit tests in this
phase use fakes and do not validate cloud credentials, IAM, indexes, or
network connectivity.

Review Google ADK's Firestore session integration documentation/source for
its collection layout, state scoping, event storage, and operational
behavior before production rollout.


## 6. Workflow resume and execution recovery (Phases 19–21)

ADK session persistence is only one part of resuming a Creative Studio
workflow. Use the Novacore `FirestoreWorkflowStore` to load the business
workflow snapshot by its `ActivityId`. Use Runtime's execution lifecycle and
recovery services to inspect persisted execution state before deciding what
can run again.

Operational boundaries:

- ADK `FirestoreSessionService` stores ADK sessions, events, and ADK state.
- Novacore `FirestoreWorkflowStore` stores and retrieves business workflow
  records.
- Runtime owns execution lifecycle and recovery decisions.
- A persisted ADK session is not proof that a corresponding Novacore
  execution succeeded.
- A persisted execution in `RUNNING` has an uncertain outcome after a crash;
  reconcile it before retrying. Do not automatically replay it.
- Idempotency keys protect Novacore execution claims, but do not independently
  guarantee exactly-once provider execution or billing. Provider-side
  idempotency support must be verified separately.

See the Phase 19–21 architecture and operations documents for the workflow
retrieval, lifecycle, and recovery procedures.

