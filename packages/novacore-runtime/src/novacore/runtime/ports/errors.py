class RuntimePortError(Exception):
    """Base class for Runtime boundary failures."""


class WorkerNotFoundError(RuntimePortError):
    """No eligible worker was found for the requested capabilities."""


class PersistenceError(RuntimePortError):
    """A persistence adapter could not complete the requested operation."""


class GenerationError(RuntimePortError):
    """A direct model-generation adapter failed."""


class AgentExecutionError(RuntimePortError):
    """An agent-execution adapter failed."""

