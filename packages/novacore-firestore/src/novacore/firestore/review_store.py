from __future__ import annotations

from datetime import datetime
from typing import Any

from novacore.kernel.identity import ActivityId, ExecutionId, WorkId
from novacore.runtime.ports import (
    PersistenceError, ReviewRecord, ReviewStatus, ReviewStore,
)


def _doc_id(value: str) -> str:
    # Review IDs are caller-supplied, arbitrary strings; encode safely for Firestore.
    import base64
    return base64.urlsafe_b64encode(value.encode("utf-8")).decode("ascii").rstrip("=") or "_"


class FirestoreReviewStore(ReviewStore):
    """Firestore persistence adapter for Runtime-owned human review records."""

    def __init__(self, client: object | None = None) -> None:
        if client is None:
            try:
                from google.cloud import firestore
            except ImportError as exc:
                raise ImportError(
                    "Install novacore-firestore[firestore] to use FirestoreReviewStore."
                ) from exc
            client = firestore.Client()
        self._client = client

    def _ref(self, review_id: str) -> object:
        return self._client.collection("human_reviews").document(_doc_id(review_id))

    @staticmethod
    def _from_data(data: dict[str, Any]) -> ReviewRecord:
        return ReviewRecord(
            review_id=data["review_id"],
            activity_id=ActivityId(data["activity_id"]),
            work_id=WorkId(data["work_id"]),
            execution_id=ExecutionId(data["execution_id"]),
            status=ReviewStatus(data["status"]),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            reviewer_id=data.get("reviewer_id"),
            feedback=data.get("feedback"),
        )

    @staticmethod
    def _payload(record: ReviewRecord) -> dict[str, Any]:
        return {
            "review_id": record.review_id,
            "activity_id": record.activity_id.value,
            "work_id": record.work_id.value,
            "execution_id": record.execution_id.value,
            "status": record.status.value,
            "created_at": record.created_at,
            "updated_at": record.updated_at,
            "reviewer_id": record.reviewer_id,
            "feedback": record.feedback,
        }

    def create_review(self, record: ReviewRecord) -> None:
        if not isinstance(record, ReviewRecord):
            raise TypeError("record must be ReviewRecord.")
        if record.status is not ReviewStatus.PENDING:
            raise ValueError("A new review must start in PENDING status.")
        try:
            from google.cloud import firestore
            ref = self._ref(record.review_id)
            transaction = self._client.transaction()

            @firestore.transactional
            def create(tx: object) -> None:
                snapshot = ref.get(transaction=tx)
                if getattr(snapshot, "exists", False):
                    raise PersistenceError("Review ID already exists.")
                tx.create(ref, self._payload(record))

            create(transaction)
        except PersistenceError:
            raise
        except ImportError as exc:
            raise PersistenceError("Firestore SDK is required for review persistence.") from exc
        except Exception as exc:
            raise PersistenceError("Firestore could not create the review record.") from exc

    def load_review(self, review_id: str) -> ReviewRecord | None:
        if not isinstance(review_id, str) or not review_id.strip():
            raise ValueError("review_id must be a non-empty string.")
        try:
            snapshot = self._ref(review_id).get()
            if not getattr(snapshot, "exists", False):
                return None
            data = snapshot.to_dict()
            return self._from_data(dict(data)) if data is not None else None
        except Exception as exc:
            raise PersistenceError("Firestore could not load the review record.") from exc

    def transition_review(
        self, record: ReviewRecord, *, expected_status: ReviewStatus
    ) -> None:
        if not isinstance(record, ReviewRecord):
            raise TypeError("record must be ReviewRecord.")
        if not isinstance(expected_status, ReviewStatus):
            raise TypeError("expected_status must be ReviewStatus.")
        try:
            from google.cloud import firestore
            ref = self._ref(record.review_id)
            transaction = self._client.transaction()

            @firestore.transactional
            def transition(tx: object) -> None:
                snapshot = ref.get(transaction=tx)
                if not getattr(snapshot, "exists", False):
                    raise PersistenceError("Review record does not exist.")
                data = snapshot.to_dict() or {}
                if data.get("status") != expected_status.value:
                    raise PersistenceError("Review status changed concurrently.")
                tx.set(ref, self._payload(record))

            transition(transaction)
        except PersistenceError:
            raise
        except ImportError as exc:
            raise PersistenceError("Firestore SDK is required for review persistence.") from exc
        except Exception as exc:
            raise PersistenceError("Firestore could not transition the review record.") from exc

