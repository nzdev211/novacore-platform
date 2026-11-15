from __future__ import annotations

import base64
from datetime import datetime, timezone
from typing import Any

from novacore.runtime.ports import PersistenceError, RevisionInProgressError, RevisionResult


class RevisionReservationConflict(RevisionInProgressError):
    """A revision key is already reserved by an unfinished attempt."""


def _document_id(source_review_id: str, idempotency_key: str) -> str:
    raw = f"{source_review_id}\0{idempotency_key}".encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=") or "_"


class FirestoreRevisionRecordStore:
    """Firestore implementation of Runtime's RevisionRecordStore port.

    A reservation is scoped to (source_review_id, idempotency_key). A completed
    reservation stores the resulting execution/review links for safe replay.
    Unfinished reservations are deliberately not expired automatically: an
    operator must reconcile an uncertain execution before releasing one.
    """

    COLLECTION = "revision_attempts"

    def __init__(self, client: object | None = None) -> None:
        if client is None:
            try:
                from google.cloud import firestore
            except ImportError as exc:
                raise ImportError(
                    "Install novacore-firestore[firestore] to use FirestoreRevisionRecordStore."
                ) from exc
            client = firestore.Client()
        self._client = client

    def _ref(self, source_review_id: str, idempotency_key: str) -> object:
        return self._client.collection(self.COLLECTION).document(
            _document_id(source_review_id, idempotency_key)
        )

    @staticmethod
    def _validate(source_review_id: str, idempotency_key: str) -> None:
        if not isinstance(source_review_id, str) or not source_review_id.strip():
            raise ValueError("source_review_id must be a non-empty string.")
        if not isinstance(idempotency_key, str) or not idempotency_key.strip():
            raise ValueError("idempotency_key must be a non-empty string.")

    @staticmethod
    def _result(data: dict[str, Any]) -> RevisionResult:
        return RevisionResult(
            source_review_id=data["source_review_id"],
            activity_id=data["activity_id"],
            work_id=data["work_id"],
            execution_id=data["execution_id"],
            review_id=data["review_id"],
            status=data.get("status", "PENDING"),
            replayed=False,
        )

    @staticmethod
    def _load_firestore() -> Any:
        try:
            from google.cloud import firestore
        except ImportError as exc:
            raise PersistenceError("Firestore SDK is required for revision persistence.") from exc
        return firestore

    def reserve_revision(
        self, *, source_review_id: str, idempotency_key: str
    ) -> RevisionResult | None:
        self._validate(source_review_id, idempotency_key)
        firestore = self._load_firestore()
        ref = self._ref(source_review_id, idempotency_key)
        transaction = self._client.transaction()
        outcome: dict[str, Any] = {}

        @firestore.transactional
        def reserve(tx: object) -> None:
            snapshot = ref.get(transaction=tx)
            if getattr(snapshot, "exists", False):
                data = snapshot.to_dict() or {}
                if data.get("state") == "completed":
                    outcome["result"] = self._result(data)
                    return
                raise RevisionReservationConflict(
                    "This revision key is already reserved; reconcile the existing attempt."
                )
            tx.create(ref, {
                "source_review_id": source_review_id,
                "idempotency_key": idempotency_key,
                "state": "reserved",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            })

        try:
            reserve(transaction)
            return outcome.get("result")
        except RevisionReservationConflict:
            raise
        except Exception as exc:
            raise PersistenceError("Firestore could not reserve the revision key.") from exc

    def complete_revision(
        self, *, source_review_id: str, idempotency_key: str, result: RevisionResult
    ) -> None:
        self._validate(source_review_id, idempotency_key)
        if not isinstance(result, RevisionResult):
            raise TypeError("result must be RevisionResult.")
        if result.source_review_id != source_review_id:
            raise ValueError("result source_review_id does not match the reservation.")
        firestore = self._load_firestore()
        ref = self._ref(source_review_id, idempotency_key)
        transaction = self._client.transaction()
        payload = {
            "source_review_id": result.source_review_id,
            "idempotency_key": idempotency_key,
            "activity_id": result.activity_id,
            "work_id": result.work_id,
            "execution_id": result.execution_id,
            "review_id": result.review_id,
            "status": result.status,
            "state": "completed",
            "updated_at": datetime.now(timezone.utc),
        }

        @firestore.transactional
        def complete(tx: object) -> None:
            snapshot = ref.get(transaction=tx)
            if not getattr(snapshot, "exists", False):
                raise RevisionReservationConflict("Revision reservation does not exist.")
            current = snapshot.to_dict() or {}
            if current.get("source_review_id") != source_review_id or current.get("idempotency_key") != idempotency_key:
                raise RevisionReservationConflict("Revision reservation does not match.")
            if current.get("state") == "completed":
                if all(current.get(key) == payload[key] for key in (
                    "activity_id", "work_id", "execution_id", "review_id", "status"
                )):
                    return
                raise RevisionReservationConflict("Revision key was completed with a different result.")
            if current.get("state") != "reserved":
                raise RevisionReservationConflict("Revision reservation is not completable.")
            tx.set(ref, {**current, **payload})

        try:
            complete(transaction)
        except RevisionReservationConflict:
            raise
        except Exception as exc:
            raise PersistenceError("Firestore could not complete the revision record.") from exc

    def release_revision(self, *, source_review_id: str, idempotency_key: str) -> None:
        self._validate(source_review_id, idempotency_key)
        firestore = self._load_firestore()
        ref = self._ref(source_review_id, idempotency_key)
        transaction = self._client.transaction()

        @firestore.transactional
        def release(tx: object) -> None:
            snapshot = ref.get(transaction=tx)
            if not getattr(snapshot, "exists", False):
                return
            data = snapshot.to_dict() or {}
            if data.get("state") == "reserved":
                tx.delete(ref)

        try:
            release(transaction)
        except Exception as exc:
            raise PersistenceError("Firestore could not release the revision reservation.") from exc

