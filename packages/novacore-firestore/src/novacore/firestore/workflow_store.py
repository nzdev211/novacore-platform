"""Firestore implementation of the Runtime WorkflowStore port.

The SDK is imported lazily so importing novacore-firestore does not require
Google Cloud dependencies unless a Firestore store is instantiated.
"""
from __future__ import annotations

import base64
import hashlib
from datetime import datetime
from enum import Enum
from typing import Any, Mapping

from novacore.kernel.activity import Activity, ActivityStatus
from novacore.kernel.assignment import Assignment
from novacore.kernel.context import Context, ContextAttributes
from novacore.kernel.contract import Contract
from novacore.kernel.execution import Execution
from novacore.kernel.objective import Objective
from novacore.kernel.planning import Planning
from novacore.kernel.request import Request
from novacore.kernel.work import Work
from novacore.kernel.identity import (ActivityId, AssignmentId, ContextId, ContractId, ExecutionId, ObjectiveId, PlanningId, RequestId, WorkerId, WorkId)
from novacore.runtime.ports import PersistenceError, WorkflowSnapshot, WorkflowStore


def _document_id(identifier: object) -> str:
    """Encode arbitrary Identifier values into safe Firestore document IDs."""
    value = getattr(identifier, "value", None)
    if not isinstance(value, str) or not value:
        raise TypeError("Expected a domain Identifier with a non-empty string value.")
    encoded = base64.urlsafe_b64encode(value.encode("utf-8")).decode("ascii")
    encoded = encoded.rstrip("=") or "_"
    # Firestore document IDs are limited to 1,500 bytes.
    if len(encoded.encode("utf-8")) > 1500:
        return "sha256-" + hashlib.sha256(value.encode("utf-8")).hexdigest()
    return encoded


def _firestore_value(value: Any) -> Any:
    """Convert supported domain metadata into Firestore-native values."""
    if isinstance(value, Enum):
        return value.value
    if value is None or isinstance(value, (str, int, float, bool, datetime)):
        return value
    if isinstance(value, Mapping):
        return {str(key): _firestore_value(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_firestore_value(item) for item in value]
    if isinstance(value, (set, frozenset)):
        # Firestore has no set type; stable ordering makes writes deterministic.
        converted = [_firestore_value(item) for item in value]
        return sorted(converted, key=lambda item: repr(item))
    raise TypeError(f"Unsupported Firestore value: {type(value).__name__}")


def _record(identifier: object, **fields: Any) -> dict[str, Any]:
    record = {"id": identifier.value}
    record.update({key: _firestore_value(value) for key, value in fields.items()})
    return record


class FirestoreWorkflowStore(WorkflowStore):
    """Persist initial Creative Studio workflow records atomically.

    Each domain type has its own top-level collection. Initial records are
    written in one Firestore transaction. Execution is a separate write,
    intentionally performed before the external agent invocation.
    """

    _MAX_TRANSACTION_WRITES = 500

    def __init__(self, client: object | None = None) -> None:
        if client is None:
            try:
                from google.cloud import firestore
            except ImportError as exc:
                raise ImportError(
                    "Install novacore-firestore[firestore] to use FirestoreWorkflowStore."
                ) from exc
            client = firestore.Client()
        self._client = client

    def _ref(self, collection: str, identifier: object) -> object:
        return self._client.collection(collection).document(_document_id(identifier))

    def save_initial_workflow(
        self,
        *,
        request: Request,
        context: Context,
        objective: Objective,
        activity: Activity,
        planning: Planning,
        work: Work,
        contracts: tuple[Contract, ...],
        assignment: Assignment,
    ) -> None:
        if len(contracts) + 7 > self._MAX_TRANSACTION_WRITES:
            raise PersistenceError("Initial workflow exceeds Firestore transaction write limit.")

        records = [
            ("requests", request.id, _record(request.id, description=request.description)),
            ("contexts", context.id, _record(
                context.id, attributes=_firestore_value(context.attributes.values)
            )),
            ("objectives", objective.id, _record(objective.id, description=objective.description)),
            ("activities", activity.id, _record(
                activity.id,
                context_id=activity.context_id.value,
                status=activity.status.value,
                created_at=activity.created_at,
                updated_at=activity.updated_at,
                request_id=activity.request_id.value if activity.request_id else None,
                objective_id=activity.objective_id.value if activity.objective_id else None,
            )),
            ("plannings", planning.id, _record(
                planning.id,
                activity_id=planning.activity_id.value,
                objective_id=planning.objective_id.value,
                description=planning.description,
            )),
            ("works", work.id, _record(
                work.id,
                activity_id=work.activity_id.value,
                planning_id=work.planning_id.value if work.planning_id else None,
                description=work.description,
            )),
        ]
        records.extend(
            ("contracts", contract.id, _record(
                contract.id, work_id=contract.work_id.value, description=contract.description
            ))
            for contract in contracts
        )
        records.append(
            ("assignments", assignment.id, _record(
                assignment.id,
                work_id=assignment.work_id.value,
                worker_id=assignment.worker_id.value,
            ))
        )

        try:
            from google.cloud import firestore
            transaction = self._client.transaction()

            @firestore.transactional
            def commit(tx: object) -> None:
                for collection, identifier, payload in records:
                    tx.set(self._ref(collection, identifier), payload)

            commit(transaction)
        except ImportError as exc:
            raise PersistenceError(
                "Firestore SDK is required for transactional workflow persistence."
            ) from exc
        except Exception as exc:
            raise PersistenceError("Firestore could not persist the initial workflow.") from exc

    def save_execution(self, execution: Execution) -> None:
        try:
            self._ref(
                "executions", execution.id
            ).set(_record(execution.id, assignment_id=execution.assignment_id.value))
        except Exception as exc:
            raise PersistenceError("Firestore could not persist the execution.") from exc


    @staticmethod
    def _document_data(snapshot: object) -> dict[str, Any] | None:
        if snapshot is None or not getattr(snapshot, "exists", False):
            return None
        data = snapshot.to_dict()
        return dict(data) if data is not None else None

    def _load_one(self, collection: str, identifier: object) -> dict[str, Any] | None:
        return self._document_data(self._ref(collection, identifier).get())

    def _load_many(self, collection: str, field: str, value: str) -> list[dict[str, Any]]:
        query = self._client.collection(collection).where(field, "==", value)
        return [dict(item.to_dict()) for item in query.stream() if item.to_dict() is not None]

    def load_workflow(self, activity_id: ActivityId) -> WorkflowSnapshot | None:
        """Rehydrate an Activity and its related records without invoking a worker."""
        if not isinstance(activity_id, ActivityId):
            raise TypeError("activity_id must be an ActivityId.")
        try:
            activity_data = self._load_one("activities", activity_id)
            if activity_data is None:
                return None

            activity = Activity(
                id=ActivityId(activity_data["id"]),
                context_id=ContextId(activity_data["context_id"]),
                status=ActivityStatus(activity_data["status"]),
                created_at=activity_data["created_at"],
                updated_at=activity_data["updated_at"],
                request_id=RequestId(activity_data["request_id"]) if activity_data.get("request_id") else None,
                objective_id=ObjectiveId(activity_data["objective_id"]) if activity_data.get("objective_id") else None,
            )
            request_data = self._load_one("requests", activity.request_id) if activity.request_id else None
            context_data = self._load_one("contexts", activity.context_id)
            objective_data = self._load_one("objectives", activity.objective_id) if activity.objective_id else None
            if request_data is None or context_data is None or objective_data is None:
                raise PersistenceError("Workflow contains a missing Request, Context, or Objective record.")

            request = Request(RequestId(request_data["id"]), request_data["description"])
            context = Context(ContextId(context_data["id"]), ContextAttributes(context_data.get("attributes", {})))
            objective = Objective(ObjectiveId(objective_data["id"]), objective_data["description"])

            plannings = tuple(Planning(PlanningId(d["id"]), ActivityId(d["activity_id"]), ObjectiveId(d["objective_id"]), d["description"]) for d in self._load_many("plannings", "activity_id", activity_id.value))
            works = tuple(Work(WorkId(d["id"]), ActivityId(d["activity_id"]), d["description"], PlanningId(d["planning_id"]) if d.get("planning_id") else None) for d in self._load_many("works", "activity_id", activity_id.value))
            work_ids = {item.id.value for item in works}
            contracts_data = [d for work_id in work_ids for d in self._load_many("contracts", "work_id", work_id)]
            assignments_data = [d for work_id in work_ids for d in self._load_many("assignments", "work_id", work_id)]
            assignments = tuple(Assignment(AssignmentId(d["id"]), WorkId(d["work_id"]), WorkerId(d["worker_id"])) for d in assignments_data)
            executions_data = [d for item in assignments for d in self._load_many("executions", "assignment_id", item.id.value)]
            return WorkflowSnapshot(
                request=request, context=context, objective=objective, activity=activity,
                planning=plannings, works=works,
                contracts=tuple(Contract(ContractId(d["id"]), WorkId(d["work_id"]), d["description"]) for d in contracts_data),
                assignments=assignments,
                executions=tuple(Execution(ExecutionId(d["id"]), AssignmentId(d["assignment_id"])) for d in executions_data),
            )
        except PersistenceError:
            raise
        except Exception as exc:
            raise PersistenceError("Firestore could not load the workflow for resumption.") from exc

