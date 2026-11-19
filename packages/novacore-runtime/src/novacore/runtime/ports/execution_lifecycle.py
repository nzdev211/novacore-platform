from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Mapping

from novacore.kernel.identity import AssignmentId, ExecutionId


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class ExecutionRecord:
    """Runtime-owned execution lifecycle state; Kernel Execution remains unchanged."""

    execution_id: ExecutionId
    assignment_id: AssignmentId
    status: ExecutionStatus
    updated_at: datetime
    output: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    error: str | None = None
    idempotency_key: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.execution_id, ExecutionId):
            raise TypeError("execution_id must be an ExecutionId.")
        if not isinstance(self.assignment_id, AssignmentId):
            raise TypeError("assignment_id must be an AssignmentId.")
        if not isinstance(self.status, ExecutionStatus):
            raise TypeError("status must be an ExecutionStatus.")
        if not isinstance(self.updated_at, datetime):
            raise TypeError("updated_at must be a datetime.")
        if not isinstance(self.output, Mapping):
            raise TypeError("output must be a mapping.")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping.")
        if self.error is not None and not isinstance(self.error, str):
            raise TypeError("error must be a string or None.")
        if self.idempotency_key is not None and not isinstance(self.idempotency_key, str):
            raise TypeError("idempotency_key must be a string or None.")

