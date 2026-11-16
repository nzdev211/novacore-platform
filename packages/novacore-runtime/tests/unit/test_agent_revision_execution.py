from datetime import datetime, timezone

import pytest

from novacore.kernel.identity import AssignmentId, ExecutionId, WorkerId
from novacore.runtime.ports import (
    AgentExecutionResult, ExecutionStatus, RevisionSource,
)
from novacore.runtime.services import AgentRevisionExecutionPort


NOW = datetime(2026, 11, 16, tzinfo=timezone.utc)


class FakeWorkflowStore:
    def __init__(self):
        self.executions = []
        self.transitions = []

    def save_execution(self, execution):
        self.executions.append(execution)

    def transition_execution(self, record, *, expected_status):
        self.transitions.append((record, expected_status))


class FakeAgent:
    def __init__(self, result=None, error=None):
        self.result = result or AgentExecutionResult(output={"shot": "revised"}, metadata={"model": "fake"})
        self.error = error
        self.requests = []

    def execute(self, request):
        self.requests.append(request)
        if self.error:
            raise self.error
        return self.result


def source():
    return RevisionSource(
        review_id="review-1", activity_id="activity-1", work_id="work-1",
        execution_id="execution-old", review_status="CHANGES_REQUESTED",
        review_feedback="Make the lighting warmer.",
        execution_input={"brief": "Storyboard shot"},
        execution_output={"shot": "original"},
        assignment_id="assignment-1", worker_id="worker-1",
    )


def test_revision_uses_new_execution_and_existing_assignment_lifecycle():
    store = FakeWorkflowStore()
    agent = FakeAgent()
    port = AgentRevisionExecutionPort(
        workflow_store=store, agent_executor=agent,
        create_execution_id=lambda: ExecutionId("execution-new"), clock=lambda: NOW,
    )

    result = port.execute_revision(
        source=source(), additional_instructions="Use golden-hour light.",
        idempotency_key="rev-key-1",
    )

    assert result.execution_id == "execution-new"
    assert result.execution_status == "succeeded"
    assert store.executions[0].id == ExecutionId("execution-new")
    assert store.executions[0].assignment_id == AssignmentId("assignment-1")
    assert [item[0].status for item in store.transitions] == [
        ExecutionStatus.PENDING, ExecutionStatus.RUNNING, ExecutionStatus.SUCCEEDED,
    ]
    request = agent.requests[0]
    assert request.worker_id == WorkerId("worker-1")
    assert request.idempotency_key == "rev-key-1"
    assert request.input["brief"] == "Storyboard shot"
    assert request.input["revision_context"] == {
        "source_execution_id": "execution-old",
        "source_output": {"shot": "original"},
        "review_feedback": "Make the lighting warmer.",
        "additional_instructions": "Use golden-hour light.",
    }


def test_provider_failure_is_recorded_as_failed_before_propagating():
    store = FakeWorkflowStore()
    agent = FakeAgent(error=RuntimeError("provider unavailable"))
    port = AgentRevisionExecutionPort(
        workflow_store=store, agent_executor=agent,
        create_execution_id=lambda: ExecutionId("execution-new"), clock=lambda: NOW,
    )

    with pytest.raises(RuntimeError, match="provider unavailable"):
        port.execute_revision(
            source=source(), additional_instructions=None, idempotency_key="rev-key-2",
        )

    assert [item[0].status for item in store.transitions] == [
        ExecutionStatus.PENDING, ExecutionStatus.RUNNING, ExecutionStatus.FAILED,
    ]
    assert "provider unavailable" in store.transitions[-1][0].error


def test_revision_requires_host_supplied_assignment_and_worker():
    store = FakeWorkflowStore()
    port = AgentRevisionExecutionPort(
        workflow_store=store, agent_executor=FakeAgent(),
        create_execution_id=lambda: ExecutionId("execution-new"), clock=lambda: NOW,
    )
    incomplete = RevisionSource(
        review_id="review-1", activity_id="activity-1", work_id="work-1",
        execution_id="execution-old", review_status="CHANGES_REQUESTED",
        review_feedback=None, execution_input={}, execution_output={},
    )
    with pytest.raises(ValueError, match="assignment_id and worker_id"):
        port.execute_revision(
            source=incomplete, additional_instructions=None, idempotency_key="rev-key-3",
        )
    assert store.executions == []


def test_revision_rejects_reusing_source_execution_id():
    store = FakeWorkflowStore()
    port = AgentRevisionExecutionPort(
        workflow_store=store, agent_executor=FakeAgent(),
        create_execution_id=lambda: ExecutionId("execution-old"), clock=lambda: NOW,
    )
    with pytest.raises(ValueError, match="new ExecutionId"):
        port.execute_revision(
            source=source(), additional_instructions=None, idempotency_key="rev-key-4",
        )

