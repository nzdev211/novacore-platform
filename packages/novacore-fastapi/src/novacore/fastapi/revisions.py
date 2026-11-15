from typing import Any, Callable


def create_revision_router(
    *,
    create_revision: Callable[..., Any],
    authenticate_creator: Callable[..., str],
):
    """Create an authenticated endpoint for starting a revised submission.

    The host callback owns authorization, review-state validation, idempotency,
    Runtime orchestration, execution persistence, and creation of the new review.
    It receives the authenticated creator identity, never a caller-supplied one.
    """
    try:
        from fastapi import APIRouter, Depends, HTTPException
        from pydantic import BaseModel, ConfigDict, Field
    except ImportError as exc:
        raise ImportError(
            "Install novacore-fastapi[fastapi] to create revision routes."
        ) from exc

    class RevisionRequest(BaseModel):
        model_config = ConfigDict(extra="forbid")
        additional_instructions: str | None = Field(default=None, max_length=10_000)
        idempotency_key: str = Field(min_length=1, max_length=256)

    class RevisionResponse(BaseModel):
        model_config = ConfigDict(extra="forbid")
        source_review_id: str
        activity_id: str
        work_id: str
        execution_id: str
        review_id: str
        status: str
        replayed: bool = False

    router = APIRouter(prefix="/reviews", tags=["human-review-revisions"])

    @router.post("/{review_id}/revisions", response_model=RevisionResponse, status_code=202)
    def start_revision(
        review_id: str,
        payload: RevisionRequest,
        creator_id: str = Depends(authenticate_creator),
    ):
        try:
            result = create_revision(
                source_review_id=review_id,
                creator_id=creator_id,
                additional_instructions=payload.additional_instructions,
                idempotency_key=payload.idempotency_key,
            )
            if result is None:
                raise HTTPException(status_code=404, detail="Review not found.")
            if isinstance(result, RevisionResponse):
                response = result
            else:
                from dataclasses import asdict, is_dataclass
                payload_data = asdict(result) if is_dataclass(result) else result
                response = RevisionResponse.model_validate(payload_data)
            if response.source_review_id != review_id:
                raise HTTPException(status_code=409, detail="Revision source mismatch.")
            if response.status != "PENDING":
                raise HTTPException(status_code=409, detail="New review must be pending.")
            return response
        except HTTPException:
            raise
        except PermissionError:
            raise HTTPException(status_code=403, detail="Not permitted to revise this review.") from None
        except (KeyError, LookupError):
            raise HTTPException(status_code=404, detail="Review not found.") from None
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail="Revision could not be started. Check workflow status before retrying.",
            ) from exc

    return router


def create_revision_service_router(
    *,
    revision_service: Any,
    authenticate_creator: Callable[..., str],
):
    """Create the revision endpoint directly from Runtime's service.

    Unlike the callback-based factory, this adapter translates the Runtime's
    domain-specific revision errors into stable HTTP responses.
    """
    try:
        from fastapi import HTTPException
        from novacore.runtime.services.revision_workflow import (
            RevisionConflictError,
            RevisionNotAllowedError,
            RevisionWorkflowError,
        )
        from novacore.runtime.ports.revision_workflow import RevisionInProgressError
    except ImportError as exc:
        raise ImportError(
            "Install novacore-fastapi[fastapi] and novacore-runtime to create revision routes."
        ) from exc

    def invoke_service(**kwargs: Any) -> Any:
        try:
            return revision_service.create_revision(**kwargs)
        except PermissionError:
            raise HTTPException(status_code=403, detail="Not permitted to revise this review.") from None
        except RevisionNotAllowedError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from None
        except (RevisionConflictError, RevisionInProgressError) as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from None
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from None
        except RevisionWorkflowError:
            raise HTTPException(
                status_code=503,
                detail="Revision could not be completed. Check workflow status before retrying.",
            ) from None

    return create_revision_router(
        create_revision=invoke_service,
        authenticate_creator=authenticate_creator,
    )

