# Phase 13 — Runtime Orchestration

## Implemented vertical slice

One Creative Studio storyboard-shot workflow is coordinated by
`StoryboardWorkflowService.create_and_execute`.

1. Accept a command containing caller-supplied Kernel IDs and shot brief data.
2. Construct Request, Context, Objective, Activity, Planning, Work, and Contract records.
3. Query WorkerDirectory for workers with required capabilities.
4. Validate that the selected worker has every required capability.
5. Construct Assignment and Execution.
6. Persist the initial workflow records atomically.
7. Persist the Execution identity before invoking the worker.
8. Invoke AgentExecutor and return the result with the created domain records.

## Deliberate constraints

- No ID generation in Kernel or Runtime; IDs are supplied by the caller.
- Worker selection uses the first eligible worker returned. Ranking is deferred.
- Agent output is returned to the caller but not persisted.
- No Activity status transition is performed after execution.
- No retries, timeout, cancellation, streaming, progress, or human-review state.
- No Resource/blob storage contract.
- No model-generation call is made in this vertical slice; AgentExecutor is the chosen execution path.
- Persistence adapter atomicity is a contract requirement, not implemented here.

## Failure behavior

- No eligible Worker: raises `WorkerNotFoundError` before persistence.
- Initial persistence failure: raises `PersistenceError`; worker is not invoked.
- Agent execution errors propagate from the adapter boundary. Execution identity has already been persisted.

## Follow-up decisions

Before production, define idempotency/duplicate submission behavior, output persistence, human-review/resume state,
worker selection policy, and what happens when external execution fails after Execution persistence.

