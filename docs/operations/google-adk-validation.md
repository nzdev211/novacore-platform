# Google ADK live integration validation

## Scope

This guide covers operational validation of the Creative Studio Google ADK
adapter. It distinguishes three persistence concerns:

1. **ADK session persistence** — agent sessions and events managed by Google ADK.
2. **Novacore workflow persistence** — business workflow records managed through
   Runtime `WorkflowStore` and implemented by `novacore-firestore`.
3. **Execution lifecycle and recovery** — Novacore execution state and recovery
   decisions managed by Runtime and persisted by the Firestore adapter.

These concerns are related but are not interchangeable.

## 1. Install

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e packages/novacore-kernel
pip install -e packages/novacore-runtime
pip install -e 'packages/novacore-google-adk[google-adk]'
```

For Firestore-backed ADK sessions:

```bash
pip install -e 'packages/novacore-google-adk[firestore]'
```

For the Novacore Firestore workflow store, install its package and optional
Firestore dependencies as declared by `packages/novacore-firestore/pyproject.toml`.
Do not assume that installing the ADK Firestore extra also configures the
Novacore workflow store; they are separate integrations.

## 2. Configure Google AI Studio

```bash
export GOOGLE_API_KEY="..."
export NOVACORE_GEMINI_MODEL="gemini-flash-latest"
```

Or configure Vertex AI using the Google Gen AI / ADK supported environment,
including `GOOGLE_GENAI_USE_VERTEXAI=true`, `GOOGLE_CLOUD_PROJECT`,
`GOOGLE_CLOUD_LOCATION`, and Application Default Credentials.

Never put API keys or service-account files in the repository or ZIP archive.

## 3. Configure ADK sessions

The adapter supports three session backends:

- `memory` — default for local development and the proof of concept.
- `firestore` — uses Google's official ADK `FirestoreSessionService`.
- `custom` — uses an injected Google ADK `BaseSessionService` implementation.

Example configuration for Firestore-backed ADK sessions:

```python
from novacore.google_adk import GoogleADKAgentExecutor, GoogleADKConfig

executor = GoogleADKAgentExecutor.from_agent(
    agent=agent,
    config=GoogleADKConfig(
        app_name="novacore_creative_studio",
        session_backend="firestore",
        firestore_root_collection="novacore-adk-sessions",
    ),
)
```

The adapter can also receive a configured Firestore async client through
`firestore_client`. Configure Google Application Default Credentials and the
project context outside source control. The Firestore backend requires the
`novacore-google-adk[firestore]` extra.

## 4. Configure Novacore workflow persistence

The Runtime `WorkflowStore` is separate from ADK's session service. The
`FirestoreWorkflowStore` in `novacore-firestore` persists Novacore business
workflow records and supports retrieval of a workflow snapshot for reopening
and resuming the application workflow.

Use the Firestore adapter when durable workflow persistence is required. The
Creative Studio example may still use in-memory/demo implementations unless
its composition explicitly wires the Firestore adapter.

## 5. Run local preflight

```bash
python scripts/check_google_adk_environment.py
```

This checks package installation, imports, and presence of expected environment
configuration. It does not send a request to Google and cannot confirm that a
credential is valid.

## 6. Run the live Creative Studio workflow

```bash
python examples/creative_studio_e2e/run_storyboard.py
```

Expected high-level behavior:

1. Novacore creates the business workflow domain records.
2. Runtime resolves a worker and persists the initial workflow through the
   configured `WorkflowStore`.
3. `GoogleADKAgentExecutor` creates or retrieves the ADK session associated with
   the execution.
4. Google ADK invokes the configured Gemini model.
5. The adapter returns the latest non-empty text in
   `AgentExecutionResult.output["text"]`.

The example's actual persistence behavior depends on the dependencies wired by
that example. A configured Firestore package does not automatically replace a
demo in-memory store; the application composition must explicitly inject the
Firestore implementations.

## 7. Execution recovery and idempotency

Novacore execution lifecycle state is not the same as ADK session state. A
persisted execution left in `RUNNING` after a process interruption has an
uncertain external outcome. Inspect and reconcile it before attempting another
provider call.

Phase 21 adds Novacore-side idempotency reservation and recovery decisions. It
prevents conflicting Novacore claims for the same key, but it does not guarantee
exactly-once provider execution or prevent duplicate provider billing. Those
guarantees require provider-side idempotency support and appropriate adapter
behavior.

Do not automatically retry an uncertain `RUNNING` execution solely because the
application process restarted.

## 8. Troubleshooting

| Symptom | Check |
|---|---|
| `Google ADK is required` | Install `novacore-google-adk[google-adk]` in the active environment. |
| Firestore session integration import error | Install `novacore-google-adk[firestore]` and verify the supported Google ADK version. |
| Missing API key | Set `GOOGLE_API_KEY`, or configure Vertex AI and ADC. |
| Project/location error | Set `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION`. |
| Permission / authentication error | Verify the key or ADC identity has access to the selected Gemini model/API and Firestore resources. |
| Model not found | Set `NOVACORE_GEMINI_MODEL` to a model available to the configured Google endpoint. |
| Empty output | Inspect ADK events and model/provider errors; the adapter returns the latest non-empty text event. |
| Workflow not durable | Verify that the application injects `FirestoreWorkflowStore`; ADK session persistence alone does not persist Novacore workflow records. |
| Execution outcome uncertain | Inspect the Novacore execution lifecycle and reconcile the provider outcome before retrying. |

## 9. Validation status and limits

- Automated tests validate deterministic Kernel, Runtime, and adapter behavior
  using local tests and fakes.
- The preflight script validates local installation and configuration only.
- A successful live Google request requires a run with valid user credentials,
  network access, and an available model.
- Firestore Emulator tests and live Firestore tests are separate from local
  unit tests. A skipped emulator test is not evidence of cloud validation.
- Neither ADK session persistence nor Novacore workflow persistence guarantees
  exactly-once model execution.

