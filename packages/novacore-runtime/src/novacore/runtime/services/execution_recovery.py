from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from novacore.kernel.identity import ExecutionId
from novacore.runtime.ports import ExecutionRecord, ExecutionStatus, WorkflowStore


class RecoveryAction(str, Enum):
    SAFE_TO_START = "safe_to_start"
    ALREADY_SUCCEEDED = "already_succeeded"
    OUTCOME_UNCERTAIN = "outcome_uncertain"
    REQUIRES_MANUAL_REVIEW = "requires_manual_review"
    NOT_FOUND = "not_found"


@dataclass(frozen=True, slots=True)
class ExecutionRecoveryDecision:
    """Classification of a persisted execution's recovery disposition."""

    execution_id: ExecutionId
    action: RecoveryAction
    record: ExecutionRecord | None = None
    reason: str = ""


class ExecutionRecoveryService:
    """Classifies persisted executions for safe restart, reuse, or manual review."""

    def __init__(self, workflow_store: WorkflowStore) -> None:
        self._workflow_store = workflow_store

    def inspect(self, execution_id: ExecutionId) -> ExecutionRecoveryDecision:
        if not isinstance(execution_id, ExecutionId):
            raise TypeError("execution_id must be an ExecutionId.")

        record = self._workflow_store.load_execution(execution_id)
        if record is None:
            return ExecutionRecoveryDecision(
                execution_id=execution_id,
                action=RecoveryAction.NOT_FOUND,
                reason="Execution record does not exist in store.",
            )

        if record.status is ExecutionStatus.PENDING:
            return ExecutionRecoveryDecision(
                execution_id=execution_id,
                action=RecoveryAction.SAFE_TO_START,
                record=record,
                reason="Execution is pending and safe to start.",
            )
        elif record.status is ExecutionStatus.SUCCEEDED:
            return ExecutionRecoveryDecision(
                execution_id=execution_id,
                action=RecoveryAction.ALREADY_SUCCEEDED,
                record=record,
                reason="Execution already succeeded; output can be reused.",
            )
        elif record.status is ExecutionStatus.RUNNING:
            return ExecutionRecoveryDecision(
                execution_id=execution_id,
                action=RecoveryAction.OUTCOME_UNCERTAIN,
                record=record,
                reason="Execution was left in running state; provider reconciliation required.",
            )
        elif record.status is ExecutionStatus.FAILED:
            return ExecutionRecoveryDecision(
                execution_id=execution_id,
                action=RecoveryAction.REQUIRES_MANUAL_REVIEW,
                record=record,
                reason=f"Execution failed: {record.error or 'unknown error'}; manual review required.",
            )
        else:
            return ExecutionRecoveryDecision(
                execution_id=execution_id,
                action=RecoveryAction.REQUIRES_MANUAL_REVIEW,
                record=record,
                reason=f"Unknown execution status: {record.status}",
            )

