from __future__ import annotations

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


@runtime_checkable
class WorkflowStore(Protocol):
    """Persistence boundary for the first Creative Studio workflow.

    `save_initial_workflow` must persist the supplied initial records atomically.
    Implementations must not hold a transaction open during provider execution
    or human review.
    """

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
        """Atomically persist the initial workflow records."""
        ...

    def save_execution(self, execution: Execution) -> None:
        """Persist an execution identity before invoking its worker."""
        ...

