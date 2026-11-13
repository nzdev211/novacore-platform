# novacore-runtime

Provider-independent application orchestration for Novacore Platform.

## Responsibilities

- Coordinate planning, worker selection, assignment, execution, validation, and human-review gates.
- Own application ports and Runtime DTOs.
- Keep provider SDKs, web frameworks, and database drivers outside Runtime.
- Depend on Kernel domain types without making Kernel depend on Runtime.

## v0.1 contract scope

This implementation defines only the contracts needed to coordinate the first Creative Studio workflow. It does not implement orchestration policy, provider calls, persistence adapters, human-review UI, or a shot-specific content schema.

## Dependency rules

- Runtime may depend on `novacore-kernel`.
- Runtime must not import OpenAI, Anthropic, Google ADK, FastAPI, Firestore, or PostgreSQL SDKs.
- Adapters implement Runtime-owned protocols.
- Kernel never imports Runtime.

## Ports

- `ModelGenerator`: direct model generation (OpenAI/Anthropic adapter path).
- `AgentExecutor`: agent-framework execution (Google ADK adapter path).
- `WorkerDirectory`: capability-based worker discovery.
- `WorkflowStore`: initial workflow persistence, retrieval, and execution lifecycle state.

Model generation and agent execution intentionally remain separate protocols.

## First workflow

`StoryboardWorkflowService.create_and_execute` coordinates one storyboard-shot work item:
construct Kernel records, discover a capable Worker, create Assignment and Execution,
persist workflow records and the Execution identity, then invoke the AgentExecutor port.

All IDs are supplied by the caller. The first eligible Worker returned by the directory is
selected; ranking and fallback policy are intentionally deferred.

## Execution lifecycle

Runtime owns `ExecutionStatus` (`pending`, `running`, `succeeded`, `failed`) and
`ExecutionRecord`; the Kernel `Execution` remains unchanged. The store contract
uses expected-status transitions so adapters can implement compare-and-set
claims. Agent failures are persisted as `failed` before the exception is
propagated. Automatic retry and crash reconciliation are deliberately deferred.


## Human review (Phase 22)

Runtime exposes `ReviewRecord`, `ReviewStatus`, `ReviewStore`, and
`HumanReviewService` for persisted human decisions. Review records are
Runtime workflow metadata, not Kernel entities. Decisions are terminal per
review record; create a new review record for a later revision.

