from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Mapping

from novacore.kernel.activity import Activity, ActivityStatus
from novacore.kernel.assignment import Assignment
from novacore.kernel.capability import Capability
from novacore.kernel.context import Context, ContextAttributes
from novacore.kernel.contract import Contract
from novacore.kernel.execution import Execution
from novacore.kernel.identity import (
    ActivityId,
    AssignmentId,
    ContextId,
    ContractId,
    ExecutionId,
    ObjectiveId,
    PlanningId,
    RequestId,
    WorkId,
)
from novacore.kernel.objective import Objective
from novacore.kernel.planning import Planning
from novacore.kernel.request import Request
from novacore.kernel.work import Work
from novacore.runtime.ports import (
    AgentExecutionRequest,
    AgentExecutor,
    AgentExecutionResult,
    PersistenceError,
    WorkerDirectory,
    WorkflowStore,
    WorkerNotFoundError,
)


@dataclass(frozen=True, slots=True)
class StoryboardWorkflowIds:
    """Caller-supplied identities; Runtime never generates Kernel identifiers."""

    request_id: RequestId
    context_id: ContextId
    objective_id: ObjectiveId
    activity_id: ActivityId
    planning_id: PlanningId
    work_id: WorkId
    contract_ids: tuple[ContractId, ...]
    assignment_id: AssignmentId
    execution_id: ExecutionId


@dataclass(frozen=True, slots=True)
class CreateStoryboardWorkflow:
    """Input for creating and executing one storyboard-shot work item."""

    ids: StoryboardWorkflowIds
    request_description: str
    objective_description: str
    planning_description: str
    work_description: str
    contract_descriptions: tuple[str, ...]
    context_attributes: Mapping[str, object]
    required_capability_ids: frozenset
    execution_input: Mapping[str, object]
    created_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.ids, StoryboardWorkflowIds):
            raise TypeError("ids must be StoryboardWorkflowIds.")
        if not isinstance(self.created_at, datetime):
            raise TypeError("created_at must be a datetime.")
        if not isinstance(self.contract_descriptions, tuple):
            raise TypeError("contract_descriptions must be a tuple.")
        if len(self.contract_descriptions) != len(self.ids.contract_ids):
            raise ValueError("Each ContractId must have exactly one contract description.")
        if not self.contract_descriptions:
            raise ValueError("At least one contract description is required.")
        if not isinstance(self.context_attributes, Mapping):
            raise TypeError("context_attributes must be a mapping.")
        if not isinstance(self.required_capability_ids, frozenset):
            raise TypeError("required_capability_ids must be a frozenset.")
        if not self.required_capability_ids:
            raise ValueError("At least one required capability is needed.")
        if not isinstance(self.execution_input, Mapping):
            raise TypeError("execution_input must be a mapping.")
        for name in (
            "request_description",
            "objective_description",
            "planning_description",
            "work_description",
        ):
            value = getattr(self, name)
            if not isinstance(value, str):
                raise TypeError(f"{name} must be a string.")
            if not value.strip():
                raise ValueError(f"{name} cannot be empty or whitespace only.")
        if any(not isinstance(item, str) or not item.strip() for item in self.contract_descriptions):
            raise ValueError("Every contract description must be a non-empty string.")


@dataclass(frozen=True, slots=True)
class StoryboardWorkflowResult:
    request: Request
    context: Context
    objective: Objective
    activity: Activity
    planning: Planning
    work: Work
    contracts: tuple[Contract, ...]
    assignment: Assignment
    execution: Execution
    agent_result: AgentExecutionResult


class StoryboardWorkflowService:
    """Coordinates the first Creative Studio workflow without provider dependencies."""

    def __init__(
        self,
        *,
        store: WorkflowStore,
        workers: WorkerDirectory,
        agent_executor: AgentExecutor,
    ) -> None:
        self._store = store
        self._workers = workers
        self._agent_executor = agent_executor

    def create_and_execute(
        self,
        command: CreateStoryboardWorkflow,
    ) -> StoryboardWorkflowResult:
        if not isinstance(command, CreateStoryboardWorkflow):
            raise TypeError("command must be CreateStoryboardWorkflow.")

        ids = command.ids
        request = Request(ids.request_id, command.request_description)
        context = Context(ids.context_id, ContextAttributes(command.context_attributes))
        objective = Objective(ids.objective_id, command.objective_description)
        activity = Activity(
            id=ids.activity_id,
            context_id=ids.context_id,
            status=ActivityStatus.ACTIVE,
            created_at=command.created_at,
            updated_at=command.created_at,
            request_id=ids.request_id,
            objective_id=ids.objective_id,
        )
        planning = Planning(
            ids.planning_id,
            ids.activity_id,
            ids.objective_id,
            command.planning_description,
        )
        work = Work(
            ids.work_id,
            ids.activity_id,
            command.work_description,
            ids.planning_id,
        )
        contracts = tuple(
            Contract(contract_id, ids.work_id, description)
            for contract_id, description in zip(ids.contract_ids, command.contract_descriptions)
        )

        workers = self._workers.find_workers_with_capabilities(
            command.required_capability_ids
        )
        eligible = tuple(
            worker
            for worker in workers
            if command.required_capability_ids.issubset(set(worker.capability_ids))
        )
        if not eligible:
            raise WorkerNotFoundError("No worker satisfies all required capabilities.")

        # Selection is intentionally simple and deterministic; ranking policy is deferred.
        worker = eligible[0]
        assignment = Assignment(ids.assignment_id, ids.work_id, worker.id)
        execution = Execution(ids.execution_id, ids.assignment_id)

        try:
            self._store.save_initial_workflow(
                request=request,
                context=context,
                objective=objective,
                activity=activity,
                planning=planning,
                work=work,
                contracts=contracts,
                assignment=assignment,
            )
            # Persist the attempt identity before invoking an external worker.
            self._store.save_execution(execution)
        except Exception as exc:
            raise PersistenceError("Could not persist the initial workflow.") from exc

        agent_result = self._agent_executor.execute(
            AgentExecutionRequest(
                execution_id=ids.execution_id,
                assignment_id=ids.assignment_id,
                worker_id=worker.id,
                input=command.execution_input,
            )
        )

        return StoryboardWorkflowResult(
            request=request,
            context=context,
            objective=objective,
            activity=activity,
            planning=planning,
            work=work,
            contracts=contracts,
            assignment=assignment,
            execution=execution,
            agent_result=agent_result,
        )

