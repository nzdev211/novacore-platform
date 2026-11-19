from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol, runtime_checkable

from novacore.kernel.identity import ActivityId, ExecutionId, WorkId


class ReviewStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class ReviewRecord:
    """Runtime-owned review record; deliberately not a Kernel domain entity."""

    review_id: str
    activity_id: ActivityId
    work_id: WorkId
    execution_id: ExecutionId
    status: ReviewStatus
    created_at: datetime
    updated_at: datetime
    reviewer_id: str | None = None
    feedback: str | None = None

    def __post_init__(self) -> None:
        for name in ("review_id",):
            value = getattr(self, name)
            if not isinstance(value, str):
                raise TypeError(f"{name} must be a string.")
            if not value.strip():
                raise ValueError(f"{name} cannot be empty or whitespace only.")
        for name, expected in (
            ("activity_id", ActivityId),
            ("work_id", WorkId),
            ("execution_id", ExecutionId),
        ):
            if not isinstance(getattr(self, name), expected):
                raise TypeError(f"{name} must be {expected.__name__}.")
        if not isinstance(self.status, ReviewStatus):
            raise TypeError("status must be ReviewStatus.")
        if not isinstance(self.created_at, datetime) or not isinstance(self.updated_at, datetime):
            raise TypeError("created_at and updated_at must be datetime values.")
        if self.reviewer_id is not None:
            if not isinstance(self.reviewer_id, str):
                raise TypeError("reviewer_id must be a string or None.")
            if not self.reviewer_id.strip():
                raise ValueError("reviewer_id cannot be empty or whitespace only.")
        if self.feedback is not None and not isinstance(self.feedback, str):
            raise TypeError("feedback must be a string or None.")
        if self.status is ReviewStatus.PENDING and (self.reviewer_id is not None or self.feedback is not None):
            raise ValueError("A pending review cannot contain a reviewer decision.")


@runtime_checkable
class ReviewStore(Protocol):
    """Persistence port for human review records."""

    def create_review(self, record: ReviewRecord) -> None:
        """Create a new pending review; duplicate IDs must fail."""
        ...

    def load_review(self, review_id: str) -> ReviewRecord | None:
        """Load one review record."""
        ...

    def transition_review(
        self, record: ReviewRecord, *, expected_status: ReviewStatus
    ) -> None:
        """Atomically transition a review when its current status matches."""
        ...

