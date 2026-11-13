
from datetime import datetime, timezone
from typing import Any, Callable

from novacore.kernel.identity import ActivityId, ExecutionId, WorkId
from novacore.runtime.ports import ReviewRecord, ReviewStatus
from novacore.runtime.services.human_review import (
    HumanReviewService,
    ReviewConflictError,
    ReviewNotFoundError,
)


def create_human_review_router(
    *,
    review_service: HumanReviewService,
    review_store: Any,
    authenticate_reviewer: Callable[..., str],
):
    """Build authenticated review routes using caller-provided auth.

    `authenticate_reviewer` is a FastAPI dependency that must return the
    authenticated principal's stable identifier. The adapter deliberately
    does not implement authentication or authorization itself.
    """
    try:
        from fastapi import APIRouter, Depends, HTTPException, status
        from pydantic import BaseModel, ConfigDict, Field
    except ImportError as exc:
        raise ImportError(
            "Install novacore-fastapi[fastapi] to create review routes."
        ) from exc

    class SubmitReviewRequest(BaseModel):
        model_config = ConfigDict(extra="forbid")
        review_id: str = Field(min_length=1)
        activity_id: str = Field(min_length=1)
        work_id: str = Field(min_length=1)
        execution_id: str = Field(min_length=1)

    class ReviewDecisionRequest(BaseModel):
        model_config = ConfigDict(extra="forbid")
        decision: ReviewStatus
        feedback: str | None = None

    class ReviewResponse(BaseModel):
        review_id: str
        activity_id: str
        work_id: str
        execution_id: str
        status: ReviewStatus
        created_at: datetime
        updated_at: datetime
        reviewer_id: str | None = None
        feedback: str | None = None

    router = APIRouter(prefix="/reviews", tags=["human-review"])

    def serialize(record: ReviewRecord) -> ReviewResponse:
        return ReviewResponse(
            review_id=record.review_id,
            activity_id=record.activity_id.value,
            work_id=record.work_id.value,
            execution_id=record.execution_id.value,
            status=record.status,
            created_at=record.created_at,
            updated_at=record.updated_at,
            reviewer_id=record.reviewer_id,
            feedback=record.feedback,
        )

    @router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
    def submit_review(
        payload: SubmitReviewRequest,
        _reviewer_id: str = Depends(authenticate_reviewer),
    ):
        now = datetime.now(timezone.utc)
        try:
            record = ReviewRecord(
                review_id=payload.review_id,
                activity_id=ActivityId(payload.activity_id),
                work_id=WorkId(payload.work_id),
                execution_id=ExecutionId(payload.execution_id),
                status=ReviewStatus.PENDING,
                created_at=now,
                updated_at=now,
            )
            return serialize(review_service.submit_for_review(record))
        except Exception as exc:
            from novacore.runtime.ports import PersistenceError
            if isinstance(exc, PersistenceError):
                raise HTTPException(status_code=503, detail="Review persistence is unavailable.") from exc
            if isinstance(exc, (TypeError, ValueError)):
                raise HTTPException(status_code=422, detail=str(exc)) from exc
            raise HTTPException(status_code=409, detail="Review could not be created.") from exc

    @router.get("/{review_id}", response_model=ReviewResponse)
    def get_review(
        review_id: str,
        _reviewer_id: str = Depends(authenticate_reviewer),
    ):
        try:
            record = review_store.load_review(review_id)
        except Exception as exc:
            raise HTTPException(status_code=503, detail="Review persistence is unavailable.") from exc
        if record is None:
            raise HTTPException(status_code=404, detail="Review not found.")
        return serialize(record)

    @router.post("/{review_id}/decision", response_model=ReviewResponse)
    def decide_review(
        review_id: str,
        payload: ReviewDecisionRequest,
        reviewer_id: str = Depends(authenticate_reviewer),
    ):
        try:
            record = review_service.decide(
                review_id,
                reviewer_id=reviewer_id,
                decision=payload.decision,
                feedback=payload.feedback,
                decided_at=datetime.now(timezone.utc),
            )
            return serialize(record)
        except ReviewNotFoundError as exc:
            raise HTTPException(status_code=404, detail="Review not found.") from exc
        except ReviewConflictError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except (TypeError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=503, detail="Review persistence is unavailable.") from exc

    return router

