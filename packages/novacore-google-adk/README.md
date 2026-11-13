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

