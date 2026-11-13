from __future__ import annotations

from dataclasses import replace
from datetime import datetime

from novacore.runtime.ports import (
    PersistenceError,
    ReviewRecord,
    ReviewStatus,
    ReviewStore,
)


class ReviewNotFoundError(LookupError):
    """Raised when a requested review record does not exist."""


class ReviewConflictError(RuntimeError):
    """Raised when a review has already been decided or concurrently changed."""


class HumanReviewService:
    """Creates and records human decisions for generated Creative Studio work."""

    def __init__(self, store: ReviewStore) -> None:
        self._store = store

    def submit_for_review(self, record: ReviewRecord) -> ReviewRecord:
        if not isinstance(record, ReviewRecord):
            raise TypeError("record must be ReviewRecord.")
        if record.status is not ReviewStatus.PENDING:
            raise ValueError("A new review must start in PENDING status.")
        try:
            self._store.create_review(record)
        except PersistenceError:
            raise
        except Exception as exc:
            raise PersistenceError("Could not create human review record.") from exc
        return record

    def decide(
        self,
        review_id: str,
        *,
        reviewer_id: str,
        decision: ReviewStatus,
        feedback: str | None,
        decided_at: datetime,
    ) -> ReviewRecord:
        if not isinstance(decision, ReviewStatus):
            raise TypeError("decision must be ReviewStatus.")
        if decision is ReviewStatus.PENDING:
            raise ValueError("A decision must be APPROVED, CHANGES_REQUESTED, or REJECTED.")
        if not isinstance(reviewer_id, str) or not reviewer_id.strip():
            raise ValueError("reviewer_id must be a non-empty string.")
        if feedback is not None and not isinstance(feedback, str):
            raise TypeError("feedback must be a string or None.")
        if not isinstance(decided_at, datetime):
            raise TypeError("decided_at must be a datetime.")

        current = self._store.load_review(review_id)
        if current is None:
            raise ReviewNotFoundError(f"Review {review_id!r} was not found.")
        if current.status is not ReviewStatus.PENDING:
            raise ReviewConflictError("Only a PENDING review can receive a decision.")

        updated = replace(
            current,
            status=decision,
            reviewer_id=reviewer_id,
            feedback=feedback,
            updated_at=decided_at,
        )
        try:
            self._store.transition_review(updated, expected_status=ReviewStatus.PENDING)
        except PersistenceError:
            raise
        except Exception as exc:
            raise ReviewConflictError("Review was concurrently changed; reload before deciding.") from exc
        return updated

