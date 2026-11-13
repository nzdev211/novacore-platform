# Phase 15 — Creative Studio End-to-End Integration

## Objective

Demonstrate the first complete Creative Studio storyboard-shot workflow through
Novacore Runtime and a real Google ADK agent, while preserving the approved
Kernel and Runtime boundaries.

## Composition

```text
Creative Studio request
        |
        v
StoryboardWorkflowService (novacore-runtime)
        |  creates domain records, resolves Worker, persists records
        v
AgentExecutor (Runtime-owned Protocol)
        |
        v
GoogleADKAgentExecutor (novacore-google-adk)
        |  creates/reuses ADK session keyed by ExecutionId
        v
Google ADK Runner -> Storyboard Agent -> Gemini model
        |
        v
ADK events -> AgentExecutionResult -> Runtime workflow result
```

## Delivered

- Runnable example at `examples/creative_studio_e2e/run_storyboard.py`.
- Real ADK `Agent` construction and adapter wiring.
- In-memory ADK session service as the default.
- In-memory demo implementations of `WorkerDirectory` and `WorkflowStore`.
- Caller-supplied domain IDs, consistent with the Kernel rule that ID generation
  is external to the Kernel.
- Configurable Gemini model via `NOVACORE_GEMINI_MODEL`.
- Setup and run instructions in the example README.

## Explicit boundaries

- No changes to Kernel entities, identities, or invariants.
- No changes to Runtime ports or workflow orchestration contracts.
- The demo `WorkflowStore` is ephemeral and is not production persistence.
- ADK session storage is in memory; it is lost when the process exits.
- Firestore-backed ADK sessions are not implemented in this phase.
- Human review, asset/blob persistence, retries, status transitions, and
  asynchronous Runtime APIs remain deferred.

## Run the real integration

Install `novacore-google-adk[google-adk]`, configure Google AI Studio or Vertex AI
credentials, then run:

```bash
python examples/creative_studio_e2e/run_storyboard.py
```

The real model invocation requires external Google credentials and network access.
It was not executed as part of the offline unit-test validation.

## Validation

- Kernel, Runtime, and Google ADK adapter unit suites: 109 passed.
- Subtests: 124 passed.
- Example Python compilation: passed.
- ZIP integrity: verified at packaging time.

