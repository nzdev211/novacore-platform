
from dataclasses import dataclass

from .identifier import Identifier


@dataclass(frozen=True, eq=False, repr=False)
class AssignmentId(Identifier):
    """
    Strongly typed identifier for a Novacore Assignment.

    Identifies the allocation of responsibility for Work.
    """
    pass

