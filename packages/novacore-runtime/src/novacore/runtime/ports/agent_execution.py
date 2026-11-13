from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Protocol, runtime_checkable

from novacore.kernel.identity import AssignmentId, ExecutionId, WorkerId


@dataclass(frozen=True, slots=True)
class AgentExecutionRequest:
    """Input to one agent-framework execution attempt."""

    execution_id: ExecutionId
    assignment_id: AssignmentId
    worker_id: WorkerId
    input: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.execution_id, ExecutionId):
            raise TypeError("execution_id must be an ExecutionId.")
        if not isinstance(self.assignment_id, AssignmentId):
            raise TypeError("assignment_id must be an AssignmentId.")
        if not isinstance(self.worker_id, WorkerId):
            raise TypeError("worker_id must be a WorkerId.")
        if not isinstance(self.input, Mapping):
            raise TypeError("input must be a mapping.")


@dataclass(frozen=True, slots=True)
class AgentExecutionResult:
    """Completed agent-framework result in Runtime-owned terms."""

    output: Mapping[str, object] = field(default_factory=dict)
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.output, Mapping):
            raise TypeError("output must be a mapping.")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping.")


@runtime_checkable
class AgentExecutor(Protocol):
    """Port for agent frameworks such as Google ADK."""

    def execute(self, request: AgentExecutionRequest) -> AgentExecutionResult:
        """Run one agent execution; progress/cancellation are deferred."""
        ...

