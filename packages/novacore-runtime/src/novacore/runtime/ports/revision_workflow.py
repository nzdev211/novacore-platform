from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol, runtime_checkable


class RevisionInProgressError(RuntimeError):
    """An idempotency key is reserved by an unfinished revision attempt."""



@dataclass(frozen=True, slots=True)
class RevisionSource:
    """Authorized source material for one revision attempt."""

    review_id: str
    activity_id: str
    work_id: str
    execution_id: str
    review_status: str
    review_feedback: str | None
    execution_input: Mapping[str, object]
    execution_output: Mapping[str, object]
    assignment_id: str | None = None
    worker_id: str | None = None

    def __post_init__(self) -> None:
        for name in ("review_id", "activity_id", "work_id", "execution_id", "review_status"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string.")
        if not isinstance(self.execution_input, Mapping):
            raise TypeError("execution_input must be a mapping.")
        if not isinstance(self.execution_output, Mapping):
            raise TypeError("execution_output must be a mapping.")
        for name in ("assignment_id", "worker_id"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{name} must be a non-empty string or None.")


@dataclass(frozen=True, slots=True)
class RevisionExecution:
    """A newly completed execution returned by the existing Runtime execution path."""

    execution_id: str
    execution_status: str
    output: Mapping[str, object]

    def __post_init__(self) -> None:
        if not self.execution_id.strip():
            raise ValueError("execution_id cannot be empty.")
        if self.execution_status.lower() != "succeeded":
            raise ValueError("A review can only be created for a succeeded execution.")
        if not isinstance(self.output, Mapping):
            raise TypeError("output must be a mapping.")


@dataclass(frozen=True, slots=True)
class RevisionResult:
    source_review_id: str
    activity_id: str
    work_id: str
    execution_id: str
    review_id: str
    status: str = "PENDING"
    replayed: bool = False


@runtime_checkable
class RevisionSourceStore(Protocol):
    def load_revision_source(self, *, review_id: str, creator_id: str) -> RevisionSource | None:
        """Load the review and its exact execution after resource authorization."""
        ...


@runtime_checkable
class RevisionExecutionPort(Protocol):
    def execute_revision(
        self,
        *,
        source: RevisionSource,
        additional_instructions: str | None,
        idempotency_key: str,
    ) -> RevisionExecution:
        """Create a new Execution through the normal Runtime lifecycle path."""
        ...


@runtime_checkable
class RevisionRecordStore(Protocol):
    def reserve_revision(
        self, *, source_review_id: str, idempotency_key: str
    ) -> RevisionResult | None:
        """Atomically claim the key; return a completed result for safe replay.

        If another request currently owns the key, the adapter must raise a
        conflict/in-progress error instead of allowing duplicate execution.
        """
        ...

    def complete_revision(
        self, *, source_review_id: str, idempotency_key: str, result: RevisionResult
    ) -> None:
        """Atomically persist the result against the caller's reservation."""
        ...

    def release_revision(
        self, *, source_review_id: str, idempotency_key: str
    ) -> None:
        """Release a reservation only when no execution has been started."""
        ...


@runtime_checkable
class RevisionReviewCreator(Protocol):
    def create_pending_review(
        self, *, activity_id: str, work_id: str, execution_id: str,
        source_review_id: str, creator_id: str,
    ) -> str:
        """Create a new PENDING ReviewRecord and return its review ID."""
        ...

