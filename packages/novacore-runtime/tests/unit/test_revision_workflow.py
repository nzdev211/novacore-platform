from novacore.runtime.ports.revision_workflow import (
    RevisionExecution, RevisionResult, RevisionSource
)
from novacore.runtime.services.revision_workflow import (
    RevisionNotAllowedError, RevisionWorkflowService
)


class SourceStore:
    def __init__(self, source):
        self.source = source

    def load_revision_source(self, *, review_id, creator_id):
        return self.source


class Executor:
    def __init__(self):
        self.calls = []

    def execute_revision(self, **kwargs):
        self.calls.append(kwargs)
        return RevisionExecution("execution-2", "succeeded", {"shot": "revised"})


class RevisionStore:
    def __init__(self):
        self.items = {}

    def reserve_revision(self, *, source_review_id, idempotency_key):
        key = (source_review_id, idempotency_key)
        if key in self.items:
            return self.items[key]
        if key in self.reserved:
            raise RuntimeError("Revision already in progress.")
        self.reserved.add(key)
        return None

    def complete_revision(self, *, source_review_id, idempotency_key, result):
        key = (source_review_id, idempotency_key)
        self.items[key] = result
        self.reserved.discard(key)

    def release_revision(self, *, source_review_id, idempotency_key):
        self.reserved.discard((source_review_id, idempotency_key))

    def __init__(self):
        self.items = {}
        self.reserved = set()


class ReviewCreator:
    def __init__(self):
        self.calls = []

    def create_pending_review(self, **kwargs):
        self.calls.append(kwargs)
        return "review-2"


def make_service(status="CHANGES_REQUESTED"):
    source = RevisionSource(
        review_id="review-1",
        activity_id="activity-1",
        work_id="work-1",
        execution_id="execution-1",
        review_status=status,
        review_feedback="Change camera angle",
        execution_input={"brief": "A sci-fi scene"},
        execution_output={"shot": "original"},
    )
    executor, store, creator = Executor(), RevisionStore(), ReviewCreator()
    service = RevisionWorkflowService(
        source_store=SourceStore(source),
        execution_port=executor,
        revision_store=store,
        review_creator=creator,
    )
    return service, executor, store, creator


def test_revision_creates_new_execution_and_pending_review():
    service, executor, store, creator = make_service()
    result = service.create_revision(
        source_review_id="review-1", creator_id="creator-1",
        additional_instructions="Lower camera", idempotency_key="key-1"
    )
    assert result.execution_id == "execution-2"
    assert result.review_id == "review-2"
    assert result.status == "PENDING"
    assert executor.calls[0]["source"].execution_output == {"shot": "original"}
    assert creator.calls[0]["source_review_id"] == "review-1"
    assert store.items[("review-1", "key-1")] == result


def test_same_key_replays_without_second_execution():
    service, executor, _, _ = make_service()
    first = service.create_revision(
        source_review_id="review-1", creator_id="creator-1",
        additional_instructions=None, idempotency_key="key-1"
    )
    second = service.create_revision(
        source_review_id="review-1", creator_id="creator-1",
        additional_instructions=None, idempotency_key="key-1"
    )
    assert first.execution_id == second.execution_id
    assert second.replayed is True
    assert len(executor.calls) == 1


def test_review_not_changes_requested_is_rejected_before_execution():
    service, executor, _, _ = make_service("APPROVED")
    try:
        service.create_revision(
            source_review_id="review-1", creator_id="creator-1",
            additional_instructions=None, idempotency_key="key-1"
        )
    except RevisionNotAllowedError:
        pass
    else:
        raise AssertionError("Expected RevisionNotAllowedError")
    assert executor.calls == []

