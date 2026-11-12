
from dataclasses import dataclass

from .identifier import Identifier


@dataclass(frozen=True, eq=False, repr=False)
class ExecutionId(Identifier):
    """
    Strongly typed identifier for a Novacore Execution.

    Identifies an individual execution attempt.
    """
    pass

