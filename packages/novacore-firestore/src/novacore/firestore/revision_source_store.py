from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from novacore.kernel.identity import ActivityId, ExecutionId
from novacore.runtime.ports import (
    PersistenceError, RevisionSource, RevisionSourceStore, ReviewStatus,
    WorkflowStore, ReviewStore,
)


class FirestoreRevisionSourceStore(RevisionSourceStore):
    """Resolve an authorized review to its exact persisted execution.

    The authorization and execution-input callbacks are host responsibilities:
    Novacore's persisted v0.1 workflow does not define tenant membership or
    persist a canonical agent input document.
    """

    def __init__(
        self,
        *,
        review_store: ReviewStore,
        workflow_store: WorkflowStore,
        authorize: Callable[[str, str, str], bool],
        load_execution_input: Callable[[str, str], Mapping[str, object]],
    ) -> None:
        self._reviews = review_store
        self._workflows = workflow_store
        self._authorize = authorize
        self._load_execution_input = load_execution_input

    def load_revision_source(self, *, review_id: str, creator_id: str) -> RevisionSource | None:
        if not review_id.strip() or not creator_id.strip():
            raise ValueError("review_id and creator_id are required.")
        try:
            review = self._reviews.load_review(review_id)
            if review is None:
                return None
            if not self._authorize(creator_id, review.activity_id.value, review.work_id.value):
                return None
            if review.status is not ReviewStatus.CHANGES_REQUESTED:
                return RevisionSource(
                    review_id=review.review_id,
                    activity_id=review.activity_id.value,
                    work_id=review.work_id.value,
                    execution_id=review.execution_id.value,
                    review_status=review.status.value.upper(),
                    review_feedback=review.feedback,
                    execution_input={},
                    execution_output={},
                )

            workflow = self._workflows.load_workflow(review.activity_id)
            if workflow is None:
                raise PersistenceError("The review's Activity workflow could not be found.")

            execution = next(
                (item for item in workflow.executions if item.id == review.execution_id), None
            )
            lifecycle = self._workflows.load_execution(review.execution_id)
            if execution is None or lifecycle is None:
                raise PersistenceError("The exact reviewed execution is missing from the workflow store.")

            assignment = next(
                (item for item in workflow.assignments if item.id == execution.assignment_id), None
            )
            if assignment is None or assignment.work_id != review.work_id:
                raise PersistenceError("The reviewed execution does not belong to the review's Work.")
            if lifecycle.execution_id != review.execution_id or lifecycle.assignment_id != execution.assignment_id:
                raise PersistenceError("Execution lifecycle identity does not match the reviewed execution.")

            execution_input = self._load_execution_input(review.activity_id.value, review.execution_id.value)
            if not isinstance(execution_input, Mapping):
                raise PersistenceError("Execution input loader must return a mapping.")
            return RevisionSource(
                review_id=review.review_id,
                activity_id=review.activity_id.value,
                work_id=review.work_id.value,
                execution_id=review.execution_id.value,
                review_status=review.status.value.upper(),
                review_feedback=review.feedback,
                execution_input=dict(execution_input),
                execution_output=dict(lifecycle.output),
            )
        except PersistenceError:
            raise
        except Exception as exc:
            raise PersistenceError("Could not resolve the authorized revision source.") from exc

