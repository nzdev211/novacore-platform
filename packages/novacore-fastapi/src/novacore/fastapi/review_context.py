from typing import Any, Callable

def create_review_context_router(
    *,
    load_review_context: Callable[..., Any],
    authenticate_reviewer: Callable[..., str],
):
    """Create an authenticated read-only endpoint for storyboard review context.

    `load_review_context(review_id=..., reviewer_id=...)` is supplied by the
    host application. It must verify that the review exists, that the
    authenticated reviewer may access it, and that the returned execution
    belongs to that review. Asset URIs should be short-lived signed URLs or
    URLs protected by the application's normal authorization layer.
    """
    try:
        from fastapi import APIRouter, Depends, HTTPException
        from pydantic import BaseModel, ConfigDict, Field, HttpUrl
    except ImportError as exc:
        raise ImportError(
            "Install novacore-fastapi[fastapi] to create review context routes."
        ) from exc

    class AssetReference(BaseModel):
        model_config = ConfigDict(extra="forbid")
        asset_id: str = Field(min_length=1)
        label: str = Field(min_length=1)
        media_type: str = Field(min_length=1)
        uri: HttpUrl
        alt_text: str | None = None

    class ReviewContextResponse(BaseModel):
        model_config = ConfigDict(extra="forbid")
        review_id: str
        brief: str | None = None
        shot_spec: dict[str, Any] = Field(default_factory=dict)
        assets: list[AssetReference] = Field(default_factory=list)

    router = APIRouter(prefix="/reviews", tags=["human-review-context"])

    @router.get("/{review_id}/context", response_model=ReviewContextResponse)
    def get_review_context(
        review_id: str,
        reviewer_id: str = Depends(authenticate_reviewer),
    ):
        try:
            context = load_review_context(
                review_id=review_id,
                reviewer_id=reviewer_id,
            )
            if context is None:
                raise HTTPException(status_code=404, detail="Review context not found.")
            if isinstance(context, ReviewContextResponse):
                result = context
            else:
                result = ReviewContextResponse.model_validate(context)
            if result.review_id != review_id:
                raise HTTPException(status_code=404, detail="Review context not found.")
            return result
        except HTTPException:
            raise
        except (KeyError, LookupError):
            raise HTTPException(status_code=404, detail="Review context not found.") from None
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail="Review context is temporarily unavailable.",
            ) from exc

    return router

