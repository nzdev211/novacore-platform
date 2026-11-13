from datetime import datetime, timezone

import pytest

from novacore.kernel.identity import ActivityId, ExecutionId, WorkId
from novacore.runtime.ports import ReviewRecord, ReviewStatus
from novacore.runtime.services.human_review import (
    HumanReviewService, ReviewConflictError, ReviewNotFoundError,
)


class MemoryReviewStore:
    def __init__(self):
        self.records = {}

    def create_review(self, record):
        if record.review_id in self.records:
            raise RuntimeError("duplicate")
        self.records[record.review_id] = record

    def load_review(self, review_id):
        return self.records.get(review_id)

    def transition_review(self, record, *, expected_status):
        current = self.records[record.review_id]
        if current.status is not expected_status:
            raise RuntimeError("conflict")
        self.records[record.review_id] = record


def pending_review():
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return ReviewRecord(
        review_id="review-1",
        activity_id=ActivityId("activity-1"),
        work_id=WorkId("work-1"),
        execution_id=ExecutionId("execution-1"),
        status=ReviewStatus.PENDING,
        created_at=now,
        updated_at=now,
    )


def test_submit_and_approve_review():
    store = MemoryReviewStore()
    service = HumanReviewService(store)
    pending = pending_review()
    assert service.submit_for_review(pending) == pending

    decided = service.decide(
        "review-1",
        reviewer_id="human-1",
        decision=ReviewStatus.APPROVED,
        feedback="Looks good.",
        decided_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
    )
    assert decided.status is ReviewStatus.APPROVED
    assert decided.reviewer_id == "human-1"
    assert store.load_review("review-1") == decided


def test_decision_is_not_repeatable():
    store = MemoryReviewStore()
    service = HumanReviewService(store)
    service.submit_for_review(pending_review())
    service.decide(
        "review-1",
        reviewer_id="human-1",
        decision=ReviewStatus.REJECTED,
        feedback=None,
        decided_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
    )
    with pytest.raises(ReviewConflictError):
        service.decide(
            "review-1",
            reviewer_id="human-2",
            decision=ReviewStatus.APPROVED,
            feedback=None,
            decided_at=datetime(2026, 1, 3, tzinfo=timezone.utc),
        )


def test_missing_review_raises_not_found():
    service = HumanReviewService(MemoryReviewStore())
    with pytest.raises(ReviewNotFoundError):
        service.decide(
            "missing",
            reviewer_id="human-1",
            decision=ReviewStatus.APPROVED,
            feedback=None,
            decided_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
        )

