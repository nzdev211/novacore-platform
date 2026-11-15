from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable

from novacore.kernel.identity import ActivityId, ExecutionId, WorkId
from novacore.runtime.ports import ReviewRecord, ReviewStatus, ReviewStore, RevisionReviewCreator


class StoreRevisionReviewCreator(RevisionReviewCreator):
    """Create a new PENDING review using the existing ReviewStore port."""

    def __init__(
        self, *, review_store: ReviewStore, create_review_id: Callable[[], str],
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._reviews = review_store
        self._create_review_id = create_review_id
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def create_pending_review(
        self, *, activity_id: str, work_id: str, execution_id: str,
        source_review_id: str, creator_id: str,
    ) -> str:
        # source_review_id and creator_id are accepted for lineage/audit hooks;
        # the canonical ReviewRecord schema does not currently store them.
        del source_review_id, creator_id
        review_id = self._create_review_id()
        if not isinstance(review_id, str) or not review_id.strip():
            raise ValueError("Review ID factory must return a non-empty string.")
        now = self._clock()
        record = ReviewRecord(
            review_id=review_id,
            activity_id=ActivityId(activity_id),
            work_id=WorkId(work_id),
            execution_id=ExecutionId(execution_id),
            status=ReviewStatus.PENDING,
            created_at=now,
            updated_at=now,
        )
        self._reviews.create_review(record)
        return review_id

