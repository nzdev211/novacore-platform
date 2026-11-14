from typing import Any, Callable


def create_revision_history_router(
    *,
    load_revision_history: Callable[..., Any],
    authenticate_reviewer: Callable[..., str],
):
    """Expose an authorized, read-only revision lineage projection.

    The host callback owns tenant/resource authorization and persistence queries.
    It must return entries oldest-first and include the requested review.
    """
    try:
        from fastapi import APIRouter, Depends, HTTPException
        from pydantic import BaseModel, ConfigDict, Field
    except ImportError as exc:
        raise ImportError(
            "Install novacore-fastapi[fastapi] to create revision-history routes."
        ) from exc

    class RevisionHistoryEntry(BaseModel):
        model_config = ConfigDict(extra="forbid")
        review_id: str = Field(min_length=1)
        execution_id: str = Field(min_length=1)
        activity_id: str = Field(min_length=1)
        work_id: str = Field(min_length=1)
        review_status: str = Field(min_length=1)
        execution_status: str | None = None
        created_at: str = Field(min_length=1)
        source_review_id: str | None = None
        feedback: str | None = None

    class RevisionHistoryResponse(BaseModel):
        model_config = ConfigDict(extra="forbid")
        activity_id: str
        work_id: str
        entries: list[RevisionHistoryEntry]

    router = APIRouter(prefix="/reviews", tags=["human-review-revision-history"])

    @router.get("/{review_id}/history", response_model=RevisionHistoryResponse)
    def get_revision_history(
        review_id: str,
        reviewer_id: str = Depends(authenticate_reviewer),
    ):
        try:
            result = load_revision_history(
                review_id=review_id,
                reviewer_id=reviewer_id,
            )
            if result is None:
                raise HTTPException(status_code=404, detail="Review not found.")
            response = RevisionHistoryResponse.model_validate(result)
            entries = response.entries
            if not entries or not any(entry.review_id == review_id for entry in entries):
                raise HTTPException(status_code=409, detail="History does not contain the requested review.")
            if len({entry.review_id for entry in entries}) != len(entries):
                raise HTTPException(status_code=409, detail="History contains duplicate review records.")
            if len({entry.execution_id for entry in entries}) != len(entries):
                raise HTTPException(status_code=409, detail="History contains duplicate execution records.")
            if any(entry.activity_id != response.activity_id or entry.work_id != response.work_id for entry in entries):
                raise HTTPException(status_code=409, detail="History crosses Activity or Work boundaries.")
            return response
        except HTTPException:
            raise
        except PermissionError:
            raise HTTPException(status_code=403, detail="Not permitted to view this revision history.") from None
        except (KeyError, LookupError):
            raise HTTPException(status_code=404, detail="Review not found.") from None
        except ValueError:
            raise HTTPException(status_code=409, detail="Revision history is invalid.") from None
        except Exception as exc:
            raise HTTPException(status_code=503, detail="Revision history is temporarily unavailable.") from exc

    return router

