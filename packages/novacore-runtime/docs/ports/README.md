# Runtime Ports — Phase 12

The first executable Runtime port set is intentionally small:

- `ModelGenerator`: direct provider generation.
- `AgentExecutor`: agent-framework execution.
- `WorkerDirectory`: capability-based worker discovery.
- `WorkflowStore`: atomic initial workflow persistence and execution identity persistence.

These are Runtime-owned protocols. Provider/database SDK types must not cross the boundary.

## Explicitly deferred

Streaming, cancellation, async APIs, tool-call schemas, model-specific options, agent progress events,
human-review persistence, resource/blob storage, and revision policy are not specified by the first
single-shot workflow. Add them only when the next concrete use case requires them.

## Orchestrationls

`StoryboardWorkflowService` is the first vertical slice. It validates the command, creates
Kernel records, selects the first worker returned that satisfies every required capability,
persists the initial workflow and execution record, then invokes `AgentExecutor`.

The service does not generate IDs, update Activity lifecycle after execution, persist agent
output, or implement human approval. Those require explicit decisions in a later phase.

