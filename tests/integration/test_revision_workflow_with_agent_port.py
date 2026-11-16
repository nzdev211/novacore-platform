from datetime import datetime, timezone

from novacore.kernel.identity import AssignmentId, ExecutionId, WorkerId
from novacore.runtime.ports import (
    AgentExecutionResult, ExecutionStatus, RevisionResult, RevisionSource,
)
from novacore.runtime.services import AgentRevisionExecutionPort, RevisionWorkflowService


class SourceStore:
    def load_revision_source(self, *, review_id, creator_id):
        assert creator_id == "creator-1"
        return RevisionSource(
            review_id=review_id, activity_id="activity-1", work_id="work-1",
            execution_id="execution-original", review_status="CHANGES_REQUESTED",
            review_feedback="Please improve the composition.",
            execution_input={"brief": "Create a storyboard shot"},
            execution_output={"shot": "original"},
            assignment_id="assignment-1", worker_id="worker-1",
        )


class RevisionStore:
    def __init__(self):
        self.reserved = set()
        self.completed = {}

    def reserve_revision(self, *, source_review_id, idempotency_key):
        key = (source_review_id, idempotency_key)
        if key in self.completed:
            return self.completed[key]
        if key in self.reserved:
            raise RuntimeError("revision already reserved")
        self.reserved.add(key)
        return None

    def complete_revision(self, *, source_review_id, idempotency_key, result):
        self.completed[(source_review_id, idempotency_key)] = result

    def release_revision(self, *, source_review_id, idempotency_key):
        self.reserved.discard((source_review_id, idempotency_key))


class ReviewCreator:
    def create_pending_review(self, **kwargs):
        assert kwargs["execution_id"] == "execution-revision-1"
        return "review-revision-1"


class WorkflowStore:
    def __init__(self):
        self.executions = []
        self.lifecycle = {}

    def save_execution(self, execution):
        self.executions.append(execution)

    def transition_execution(self, record, *, expected_status):
        current = self.lifecycle.get(record.execution_id.value)
        current_status = current.status if current else None
        assert current_status is expected_status
        self.lifecycle[record.execution_id.value] = record


class Agent:
    def __init__(self):
        self.requests = []

    def execute(self, request):
        self.requests.append(request)
        return AgentExecutionResult(
            output={"shot": "revised", "quality": "approved-for-review"},
            metadata={"provider": "test-double"},
        )


def test_revision_service_runs_new_execution_through_runtime_lifecycle():
    workflow_store = WorkflowStore()
    agent = Agent()
    execution_port = AgentRevisionExecutionPort(
        workflow_store=workflow_store,
        agent_executor=agent,
        create_execution_id=lambda: ExecutionId("execution-revision-1"),
        clock=lambda: datetime(2026, 11, 16, tzinfo=timezone.utc),
    )
    revision_store = RevisionStore()
    service = RevisionWorkflowService(
        source_store=SourceStore(), execution_port=execution_port,
        revision_store=revision_store, review_creator=ReviewCreator(),
    )

    result = service.create_revision(
        source_review_id="review-original", creator_id="creator-1",
        additional_instructions="Use a warmer palette.", idempotency_key="revision-key-1",
    )

    assert result == RevisionResult(
        source_review_id="review-original", activity_id="activity-1", work_id="work-1",
        execution_id="execution-revision-1", review_id="review-revision-1",
    )
    assert [item.status for item in workflow_store.lifecycle.values()] == [ExecutionStatus.SUCCEEDED]
    assert workflow_store.executions[0].id == ExecutionId("execution-revision-1")
    request = agent.requests[0]
    assert request.assignment_id == AssignmentId("assignment-1")
    assert request.worker_id == WorkerId("worker-1")
    assert request.input["revision_context"]["review_feedback"] == "Please improve the composition."
    assert request.input["revision_context"]["additional_instructions"] == "Use a warmer palette."
    assert revision_store.completed[("review-original", "revision-key-1")] == result

