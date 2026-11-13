from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from novacore.kernel.activity import Activity
from novacore.kernel.assignment import Assignment
from novacore.kernel.context import Context
from novacore.kernel.contract import Contract
from novacore.kernel.execution import Execution
from novacore.kernel.objective import Objective
from novacore.kernel.planning import Planning
from novacore.kernel.request import Request
from novacore.kernel.work import Work
from novacore.kernel.identity import ActivityId, ExecutionId
from .execution_lifecycle import ExecutionRecord, ExecutionStatus


@dataclass(frozen=True, slots=True)
class WorkflowSnapshot:
    """Rehydrated business records needed to reopen a persisted workflow."""

    request: Request
    context: Context
    objective: Objective
    activity: Activity
    planning: tuple[Planning, ...]
    works: tuple[Work, ...]
    contracts: tuple[Contract, ...]
    assignments: tuple[Assignment, ...]
    executions: tuple[Execution, ...]
    execution_records: tuple[ExecutionRecord, ...] = ()


@runtime_checkable
class WorkflowStore(Protocol):
    """Persistence boundary for Creative Studio business workflow records."""

    def save_initial_workflow(
        self, *, request: Request, context: Context, objective: Objective,
        activity: Activity, planning: Planning, work: Work,
        contracts: tuple[Contract, ...], assignment: Assignment,
    ) -> None:
        """Atomically persist the initial workflow records."""
        ...

    def save_execution(self, execution: Execution) -> None:
        """Persist an execution identity before invoking its worker."""
        ...

    def transition_execution(
        self, record: ExecutionRecord, *, expected_status: ExecutionStatus | None
    ) -> None:
        """Atomically create/update lifecycle state if the current status matches."""
        ...

    def load_execution(self, execution_id: ExecutionId) -> ExecutionRecord | None:
        """Load lifecycle metadata for one execution attempt."""
        ...

    def load_workflow(self, activity_id: ActivityId) -> WorkflowSnapshot | None:
        """Load all persisted records associated with an Activity for resumption."""
        ...

