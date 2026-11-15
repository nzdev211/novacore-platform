from datetime import datetime, timezone
from types import SimpleNamespace

from novacore.kernel.identity import ActivityId, AssignmentId, ExecutionId, WorkId
from novacore.runtime.ports import ReviewStatus
from novacore.firestore.revision_source_store import FirestoreRevisionSourceStore
from novacore.firestore.revision_review_creator import StoreRevisionReviewCreator


class FakeReviewStore:
    def __init__(self, review):
        self.review = review
        self.created = []

    def load_review(self, review_id):
        return self.review if self.review and self.review.review_id == review_id else None

    def create_review(self, record):
        self.created.append(record)


class FakeWorkflowStore:
    def __init__(self, workflow, lifecycle):
        self.workflow = workflow
        self.lifecycle = lifecycle

    def load_workflow(self, activity_id):
        return self.workflow if activity_id == self.workflow.activity.id else None

    def load_execution(self, execution_id):
        return self.lifecycle if execution_id == self.lifecycle.execution_id else None


def make_source_parts(status=ReviewStatus.CHANGES_REQUESTED):
    activity_id = ActivityId("activity-1")
    work_id = WorkId("work-1")
    execution_id = ExecutionId("execution-1")
    assignment_id = AssignmentId("assignment-1")
    review = SimpleNamespace(
        review_id="review-1", activity_id=activity_id, work_id=work_id,
        execution_id=execution_id, status=status, feedback="Make the lighting warmer",
    )
    execution = SimpleNamespace(id=execution_id, assignment_id=assignment_id)
    assignment = SimpleNamespace(id=assignment_id, work_id=work_id)
    workflow = SimpleNamespace(
        activity=SimpleNamespace(id=activity_id), executions=(execution,), assignments=(assignment,),
    )
    lifecycle = SimpleNamespace(
        execution_id=execution_id, assignment_id=assignment_id,
        output={"shot_spec": {"camera": "wide"}},
    )
    return review, workflow, lifecycle


def test_source_store_loads_exact_execution_and_input():
    review, workflow, lifecycle = make_source_parts()
    store = FirestoreRevisionSourceStore(
        review_store=FakeReviewStore(review),
        workflow_store=FakeWorkflowStore(workflow, lifecycle),
        authorize=lambda creator, activity, work: creator == "creator-1",
        load_execution_input=lambda activity, execution: {"brief": "A sci-fi scene"},
    )
    source = store.load_revision_source(review_id="review-1", creator_id="creator-1")
    assert source.execution_id == "execution-1"
    assert source.execution_input == {"brief": "A sci-fi scene"}
    assert source.execution_output == {"shot_spec": {"camera": "wide"}}
    assert source.review_feedback == "Make the lighting warmer"


def test_source_store_hides_unauthorized_review():
    review, workflow, lifecycle = make_source_parts()
    store = FirestoreRevisionSourceStore(
        review_store=FakeReviewStore(review),
        workflow_store=FakeWorkflowStore(workflow, lifecycle),
        authorize=lambda *_: False,
        load_execution_input=lambda *_: {},
    )
    assert store.load_revision_source(review_id="review-1", creator_id="other") is None


def test_source_store_does_not_load_input_for_ineligible_review():
    review, workflow, lifecycle = make_source_parts(ReviewStatus.APPROVED)
    called = []
    store = FirestoreRevisionSourceStore(
        review_store=FakeReviewStore(review),
        workflow_store=FakeWorkflowStore(workflow, lifecycle),
        authorize=lambda *_: True,
        load_execution_input=lambda *_: called.append(True) or {},
    )
    source = store.load_revision_source(review_id="review-1", creator_id="creator")
    assert source.review_status == "APPROVED"
    assert called == []


def test_review_creator_uses_existing_review_store():
    review_store = FakeReviewStore(None)
    now = datetime(2026, 11, 14, tzinfo=timezone.utc)
    creator = StoreRevisionReviewCreator(
        review_store=review_store, create_review_id=lambda: "review-2", clock=lambda: now,
    )
    result = creator.create_pending_review(
        activity_id="activity-1", work_id="work-1", execution_id="execution-2",
        source_review_id="review-1", creator_id="creator-1",
    )
    assert result == "review-2"
    record = review_store.created[0]
    assert record.status is ReviewStatus.PENDING
    assert record.execution_id == ExecutionId("execution-2")
    assert record.created_at == now

