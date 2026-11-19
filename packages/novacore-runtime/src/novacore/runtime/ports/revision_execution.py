from __future__ import annotations

from collections.abc import Callable, Mapping

from novacore.runtime.ports.revision_workflow import RevisionExecution, RevisionExecutionPort, RevisionSource


class CallbackRevisionExecutionPort(RevisionExecutionPort):
    """Bridge revisions to the application's existing Runtime execution path.

    The callback must create a new Kernel Execution and use the existing
    WorkflowStore lifecycle/idempotency path. It must not call an agent SDK
    directly or reuse the source Execution ID.
    """

    def __init__(
        self,
        execute: Callable[[RevisionSource, str | None, str], tuple[str, str, Mapping[str, object]]],
    ) -> None:
        self._execute = execute

    def execute_revision(
        self, *, source: RevisionSource, additional_instructions: str | None,
        idempotency_key: str,
    ) -> RevisionExecution:
        execution_id, status, output = self._execute(source, additional_instructions, idempotency_key)
        return RevisionExecution(
            execution_id=execution_id,
            execution_status=status,
            output=output,
        )

