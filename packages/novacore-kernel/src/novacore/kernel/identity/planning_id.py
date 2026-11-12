
from dataclasses import dataclass

from .identifier import Identifier


@dataclass(frozen=True, eq=False, repr=False)
class PlanningId(Identifier):
    """
    Strongly typed identifier for a Novacore Planning record.
    """
    pass
