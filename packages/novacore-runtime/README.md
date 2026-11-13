# novacore-runtime

Provider-independent application orchestration for Novacore Platform.

## Responsibilities

- Coordinate planning, worker selection, assignment, execution, validation, and human-review gates.
- Own application ports and Runtime DTOs.
- Keep provider SDKs, web frameworks, and database drivers outside Runtime.
- Depend on Kernel domain types without making Kernel depend on Runtime.

## v0.1 contract scope

This implementation defines the contracts and orchestration needed to coordinate the first Creative Studio workflow. Persistence implementations remain in adapters; Runtime coordinates their use. Human-review UI and a shot-specific content schema remain out of scope.

## Dependency rules

- Runtime may depend on `novacore-kernel`.
- Runtime must not import OpenAI, Anthropic, Google ADK, FastAPI, Firestore, or PostgreSQL SDKs.
- Adapters implement Runtime-owned protocols.
- Kernel never imports Runtime.

## Ports

- `ModelGenerator`: direct model generation (OpenAI/Anthropic adapter path).
- `AgentExecutor`: agent-framework execution (Google ADK adapter path).
- `WorkerDirectory`: capability-based worker discovery.
- `WorkflowStore`: workflow persistence and retrieval, plus execution lifecycle persistence.

Model generation and agent execution intentionally remain separate protocols.

## First workflow

`StoryboardWorkflowService.create_and_execute` coordinates one storyboard-shot work item: construct Kernel records, discover a capable Worker, create Assignment and Execution, persist workflow records and the Execution identity, then invoke the AgentExecutor port.

All IDs are supplied by the caller. The first eligible Worker returned by the directory is selected; ranking and fallback policy are intentionally deferred.

## Execution lifecycle and recovery

Runtime owns `ExecutionStatus` (`pending`, `running`, `succeeded`, `failed`) and `ExecutionRecord`; the Kernel `Execution` remains unchanged. Expected-status transitions allow adapters to implement compare-and-set claims. Agent failures are persisted as `failed` before the exception is propagated.

`ExecutionRecoveryService` classifies persisted state but does not automatically retry provider calls. A `RUNNING` execution after interruption is outcome-uncertain. Firestore idempotency-key reservation prevents a different Novacore ExecutionId from claiming the same key; it does not guarantee exactly-once provider execution or billing.

