# Google ADK live integration validation

## Scope

Phase 16 hardens the operational path for the Creative Studio Google ADK proof
of concept. It does not change Kernel entities, Runtime ports, or workflow
orchestration.

The local test suite uses fakes and does not call Google. A live run requires
Google credentials, network access, and an installed `google-adk` extra.

## 1. Install

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e packages/novacore-kernel
pip install -e packages/novacore-runtime
pip install -e 'packages/novacore-google-adk[google-adk]'
```

## 2. Configure Google AI Studio

```bash
export GOOGLE_API_KEY="..."
export NOVACORE_GEMINI_MODEL="gemini-flash-latest"
```

Or configure Vertex AI using the Google Gen AI / ADK supported environment,
including `GOOGLE_GENAI_USE_VERTEXAI=true`, `GOOGLE_CLOUD_PROJECT`,
`GOOGLE_CLOUD_LOCATION`, and Application Default Credentials.

Never put API keys or service-account files in the repository or ZIP archive.

## 3. Run local preflight

```bash
python scripts/check_google_adk_environment.py
```

This checks package installation, imports, and presence of expected environment
configuration. It does not send a request to Google and cannot confirm that a
credential is valid.

## 4. Run the live Creative Studio workflow

```bash
python examples/creative_studio_e2e/run_storyboard.py
```

Expected high-level result:

1. Novacore creates the workflow domain records.
2. Runtime resolves the demo worker and persists the initial workflow/execution
   using the in-memory demo store.
3. `GoogleADKAgentExecutor` creates or retrieves the ADK session for the
   execution.
4. Google ADK invokes the configured Gemini model.
5. The adapter returns the latest non-empty text in
   `AgentExecutionResult.output["text"]`.

The example prints the Activity, Assignment, Execution, and generated text.
A successful live run is the point at which the external model integration is
validated. The offline test suite alone is not evidence of a successful live
Gemini call.

## 5. Session and persistence boundaries

- ADK sessions default to `InMemorySessionService`.
- The adapter can accept a custom ADK `BaseSessionService`.
- Google ADK currently documents in-memory, SQL database, and Vertex AI session
  services. It does not provide a built-in Firestore session service.
- Firestore support therefore requires a separately implemented and tested
  adapter of the ADK session-service contract.
- The example's Runtime `WorkflowStore` and `WorkerDirectory` are demo fakes.
  They are not durable and must not be used as production persistence.

## Troubleshooting

| Symptom | Check |
|---|---|
| `Google ADK is required` | Install `novacore-google-adk[google-adk]` in the active environment. |
| Missing API key | Set `GOOGLE_API_KEY`, or configure Vertex AI and ADC. |
| Project/location error | Set `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION`. |
| Permission / authentication error | Verify the key or ADC identity has access to the selected Gemini model/API. |
| Model not found | Set `NOVACORE_GEMINI_MODEL` to a model available to the configured Google endpoint. |
| Empty output | Inspect ADK events and model/provider errors; the adapter returns the latest non-empty text event. |

## Validation status for this archive

- Automated Kernel, Runtime, and Google ADK adapter tests are run locally.
- The live Google request is not run in this environment because Google ADK
dependencies and user credentials are not present.
- No Firestore session service or durable Runtime workflow store is claimed as
  implemented by this phase.

