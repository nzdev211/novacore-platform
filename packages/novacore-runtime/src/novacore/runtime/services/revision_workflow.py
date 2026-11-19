from __future__ import annotations

from dataclasses import replace
from typing import Any

from novacore.runtime.ports.revision_workflow import (
    RevisionExecutionPort,
    RevisionInProgressError,
    RevisionRecordStore,
    RevisionResult,
    RevisionReviewCreator,
    RevisionSourceStore,
)


class RevisionConflictError(RuntimeError):
    """An idempotency conflict or concurrent attempt occurred."""


class RevisionNotAllowedError(RuntimeError):
    """The source review cannot be revised in its current state."""


class RevisionWorkflowError(RuntimeError):
    """A failure occurred while orchestrating the revision workflow."""


class RevisionWorkflowService:
    """Orchestrates an authenticated revision of previous reviewed work."""

    def __init__(
        self,
        *,
        source_store: RevisionSourceStore,
        execution_port: RevisionExecutionPort,
        revision_store: RevisionRecordStore,
        review_creator: RevisionReviewCreator,
    ) -> None:
        self._source_store = source_store
        self._execution_port = execution_port
        self._revision_store = revision_store
        self._review_creator = review_creator

    def create_revision(
        self,
        *,
        source_review_id: str,
        creator_id: str,
        idempotency_key: str,
        additional_instructions: str | None = None,
    ) -> RevisionResult:
        if not isinstance(source_review_id, str) or not source_review_id.strip():
            raise ValueError("source_review_id must be a non-empty string.")
        if not isinstance(creator_id, str) or not creator_id.strip():
            raise ValueError("creator_id must be a non-empty string.")
        if not isinstance(idempotency_key, str) or not idempotency_key.strip():
            raise ValueError("idempotency_key must be a non-empty string.")

        try:
            cached = self._revision_store.reserve_revision(
                source_review_id=source_review_id,
                idempotency_key=idempotency_key,
            )
        except RevisionInProgressError as exc:
            raise RevisionConflictError(str(exc)) from exc
        except Exception as exc:
            if "reserved" in str(exc).lower() or "progress" in str(exc).lower():
                raise RevisionConflictError(str(exc)) from exc
            raise

        if cached is not None:
            if isinstance(cached, RevisionResult):
                return replace(cached, replayed=True)
            return cached

        # Validation phase: if validation fails, release reservation
        try:
            source = self._source_store.load_revision_source(
                review_id=source_review_id,
                creator_id=creator_id,
            )
            if source is None:
                self._revision_store.release_revision(
                    source_review_id=source_review_id,
                    idempotency_key=idempotency_key,
                )
                raise LookupError(f"Review {source_review_id} not found.")

            if source.review_status != "CHANGES_REQUESTED":
                self._revision_store.release_revision(
                    source_review_id=source_review_id,
                    idempotency_key=idempotency_key,
                )
                raise RevisionNotAllowedError(
                    f"Review {source_review_id} status is {source.review_status}, "
                    "not CHANGES_REQUESTED."
                )
        except (LookupError, RevisionNotAllowedError, ValueError, PermissionError):
            raise
        except Exception as exc:
            self._revision_store.release_revision(
                source_review_id=source_review_id,
                idempotency_key=idempotency_key,
            )
            raise RevisionWorkflowError(str(exc)) from exc

        # Execution phase: keep reservation for reconciliation on failure
        try:
            execution = self._execution_port.execute_revision(
                source=source,
                additional_instructions=additional_instructions,
                idempotency_key=idempotency_key,
            )
        except Exception as exc:
            raise RevisionWorkflowError(f"Execution failed: {exc}") from exc

        # Review creation phase
        try:
            new_review_id = self._review_creator.create_pending_review(
                activity_id=source.activity_id,
                work_id=source.work_id,
                execution_id=execution.execution_id,
                source_review_id=source.review_id,
                creator_id=creator_id,
            )
        except Exception as exc:
            raise RevisionWorkflowError(f"Review creation failed: {exc}") from exc

        result = RevisionResult(
            source_review_id=source.review_id,
            activity_id=source.activity_id,
            work_id=source.work_id,
            execution_id=execution.execution_id,
            review_id=new_review_id,
            status="PENDING",
            replayed=False,
        )

        self._revision_store.complete_revision(
            source_review_id=source.review_id,
            idempotency_key=idempotency_key,
            result=result,
        )
        return result

