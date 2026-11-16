from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

from novacore.kernel.execution import Execution
from novacore.kernel.identity import AssignmentId, ExecutionId, WorkerId
from novacore.runtime.ports import (
    AgentExecutionRequest, AgentExecutor, ExecutionRecord, ExecutionStatus,
    RevisionExecution, RevisionExecutionPort, RevisionSource, WorkflowStore,
)


class AgentRevisionExecutionPort(RevisionExecutionPort):
    """Run a revision through the existing Runtime lifecycle and AgentExecutor.

    ID creation remains outside the Runtime: ``create_execution_id`` is a
    host-supplied factory. The original Assignment is reused because a Work can
    have multiple Execution attempts. No provider SDK is imported here.
    """

    def __init__(
        self, *, workflow_store: WorkflowStore, agent_executor: AgentExecutor,
        create_execution_id: Callable[[], ExecutionId],
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if workflow_store is None or agent_executor is None:
            raise TypeError("workflow_store and agent_executor are required.")
        if not callable(create_execution_id):
            raise TypeError("create_execution_id must be callable.")
        self._store = workflow_store
        self._agent = agent_executor
        self._create_execution_id = create_execution_id
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def execute_revision(
        self, *, source: RevisionSource, additional_instructions: str | None,
        idempotency_key: str,
    ) -> RevisionExecution:
        if not isinstance(source, RevisionSource):
            raise TypeError("source must be RevisionSource.")
        if not source.assignment_id or not source.worker_id:
            raise ValueError("Revision source must include its original assignment_id and worker_id.")
        execution_id = self._create_execution_id()
        if not isinstance(execution_id, ExecutionId):
            raise TypeError("create_execution_id must return ExecutionId.")
        if execution_id.value == source.execution_id:
            raise ValueError("A revision must use a new ExecutionId.")

        assignment_id = AssignmentId(source.assignment_id)
        worker_id = WorkerId(source.worker_id)
        execution = Execution(execution_id, assignment_id)
        now = self._clock()

        # Persist identity and PENDING before claiming RUNNING or calling an agent.
        self._store.save_execution(execution)
        self._store.transition_execution(
            ExecutionRecord(
                execution_id=execution_id, assignment_id=assignment_id,
                status=ExecutionStatus.PENDING, updated_at=now,
                idempotency_key=idempotency_key,
            ),
            expected_status=None,
        )
        self._store.transition_execution(
            ExecutionRecord(
                execution_id=execution_id, assignment_id=assignment_id,
                status=ExecutionStatus.RUNNING, updated_at=self._clock(),
                idempotency_key=idempotency_key,
            ),
            expected_status=ExecutionStatus.PENDING,
        )

        execution_input: dict[str, Any] = dict(source.execution_input)
        execution_input["revision_context"] = {
            "source_execution_id": source.execution_id,
            "source_output": dict(source.execution_output),
            "review_feedback": source.review_feedback,
            "additional_instructions": additional_instructions,
        }
        try:
            result = self._agent.execute(
                AgentExecutionRequest(
                    execution_id=execution_id, assignment_id=assignment_id,
                    worker_id=worker_id, input=execution_input,
                    idempotency_key=idempotency_key,
                )
            )
        except Exception as exc:
            self._store.transition_execution(
                ExecutionRecord(
                    execution_id=execution_id, assignment_id=assignment_id,
                    status=ExecutionStatus.FAILED, updated_at=self._clock(),
                    error=f"{type(exc).__name__}: {exc}",
                    idempotency_key=idempotency_key,
                ),
                expected_status=ExecutionStatus.RUNNING,
            )
            raise

        self._store.transition_execution(
            ExecutionRecord(
                execution_id=execution_id, assignment_id=assignment_id,
                status=ExecutionStatus.SUCCEEDED, updated_at=self._clock(),
                output=result.output, metadata=result.metadata,
                idempotency_key=idempotency_key,
            ),
            expected_status=ExecutionStatus.RUNNING,
        )
        return RevisionExecution(
            execution_id=execution_id.value, execution_status="succeeded",
            output=result.output,
        )

