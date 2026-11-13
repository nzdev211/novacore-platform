# novacore-google-adk

Google ADK adapter implementing the Novacore Runtime `AgentExecutor` protocol.

## Install

```bash
pip install -e packages/novacore-runtime
pip install -e 'packages/novacore-google-adk[google-adk]'
```

## In-memory (default)

```python
from google.adk.agents import Agent
from novacore.google_adk import GoogleADKAgentExecutor, GoogleADKConfig

agent = Agent(
    name="storyboard_agent",
    model="gemini-2.5-flash",
    instruction="Create one concise storyboard shot package from the supplied input.",
)
executor = GoogleADKAgentExecutor.from_agent(
    agent=agent,
    config=GoogleADKConfig(app_name="novacore_creative_studio"),
)
```

Pass `executor` to `StoryboardWorkflowService(agent_executor=executor)`.

## Custom persistent session service

```python
executor = GoogleADKAgentExecutor.from_agent(
    agent=agent,
    config=GoogleADKConfig(
        app_name="novacore_creative_studio",
        session_backend="custom",
    ),
    session_service=my_adk_session_service,
)
```

`my_adk_session_service` must implement Google ADK's session-service contract. This is the extension point for a future Firestore-backed service. This package does **not** include a Firestore implementation. Keep that implementation in the infrastructure integration layer, not Kernel.

## Mapping

- `ExecutionId.value` -> ADK `session_id`
- `WorkerId.value` with configured prefix -> ADK `user_id`
- Execution, assignment, worker IDs and Runtime input -> JSON user message
- Latest non-empty event text -> `AgentExecutionResult.output["text"]`
- Provider, app, session and event count -> result metadata

Runtime's v0.1 port is synchronous; this adapter bridges ADK's asynchronous `run_async`. Streaming, cancellation, retries, progress callbacks, and output persistence are deferred.

# novacore-google-adk

Google Agent Development Kit (ADK) adapter implementing Runtime's
`AgentExecutor` port.

## Session backends

The adapter supports three backends:

| Backend | Purpose | Install |
|---|---|---|
| `memory` | Local development and POC; default | `novacore-google-adk[google-adk]` |
| `firestore` | Durable ADK sessions and events | `novacore-google-adk[firestore]` |
| `custom` | User-supplied ADK `BaseSessionService` | `novacore-google-adk[google-adk]` |

Firestore session storage uses Google's official Python ADK
`FirestoreSessionService` integration, not a Novacore-maintained
reimplementation of ADK's session protocol.

## Install

In addition to Kernel and Runtime:

```bash
pip install -e packages/novacore-kernel
pip install -e packages/novacore-runtime
pip install -e 'packages/novacore-google-adk[google-adk]'
```

For Firestore:

```bash
pip install -e 'packages/novacore-google-adk[firestore]'
```

The Firestore extra uses Google ADK 2.14 or newer (within the 2.x major
version) and `google-cloud-firestore`.

## In-memory (default)

```python
from google.adk.agents import Agent
from novacore.google_adk import GoogleADKAgentExecutor, GoogleADKConfig

agent = Agent(
    name="storyboard_agent",
    model="gemini-2.5-flash",
    instruction="Create one concise storyboard shot package from the supplied input.",
)

executor = GoogleADKAgentExecutor.from_agent(
    agent=agent,
    config=GoogleADKConfig(app_name="novacore_creative_studio"),
)
```

## Firestore-backed ADK sessions

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

The official ADK integration constructs an async Firestore client using
Application Default Credentials. To inject a configured client:

```python
executor = GoogleADKAgentExecutor.from_agent(
    agent=agent,
    config=GoogleADKConfig(
        app_name="novacore_creative_studio",
        session_backend="firestore",
    ),
    firestore_client=firestore_async_client,
)
```

## Custom session service

```python
executor = GoogleADKAgentExecutor.from_agent(
    agent=agent,
    config=GoogleADKConfig(
        app_name="novacore_creative_studio",
        session_backend="custom",
    ),
    session_service=my_adk_base_session_service,
)
```

## Firestore setup

Configure Application Default Credentials and project context outside source
control. For local development:

```bash
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT="your-project-id"
```

Set `firestore_root_collection` to isolate the ADK session hierarchy. The
official integration stores session documents and event subcollections, and
handles ADK state scopes and event appends. Configure Firestore security
rules/IAM and indexes according to the official ADK integration and your
deployment requirements.

## Persistence boundary

- `novacore-firestore.FirestoreWorkflowStore` persists Novacore business
  workflow records through Runtime's `WorkflowStore`.
- ADK `FirestoreSessionService` persists ADK sessions, state, and event
  history.
- These are separate collections and separate responsibilities.
- Runtime's `WorkflowStore` now supports loading a persisted workflow by
  `ActivityId` (Phase 19), in addition to the original write operation.
- Runtime execution lifecycle and recovery decisions are separate from ADK
  session persistence (Phases 20–21). A persisted ADK session does not by
  itself prove that a Novacore execution completed successfully.
- Keep the two Firestore collection hierarchies separate. Do not treat ADK
  session history as the authoritative business workflow record.
- Kernel domain objects remain unchanged; lifecycle and recovery policy live
  in Runtime, while Firestore adapters persist their respective records.

## Execution mapping

- `execution_id.value` becomes the ADK session ID.
- `worker_id.value` (with a configurable prefix) becomes the ADK user ID.
- Assignment, execution, worker IDs, and Runtime input are serialized into
  the ADK user message.
- Latest non-empty text from the ADK event stream becomes
  `AgentExecutionResult.output["text"]`.

The Runtime port is synchronous in v0.1. The adapter bridges ADK's async
`run_async` API. Streaming, cancellation, progress callbacks, and artifact
storage remain out of scope. Runtime workflow retrieval and execution recovery
are handled by the Runtime and workflow-persistence components, not by this
ADK adapter. See `docs/architecture/phase-19-workflow-retrieval-and-resume.md`,
`docs/architecture/phase-20-execution-lifecycle-and-recovery.md`, and
`docs/architecture/phase-21-execution-recovery-idempotency.md`.

## Credentials

Use Application Default Credentials or the deployment's workload identity.
Never commit service-account keys or API keys.

