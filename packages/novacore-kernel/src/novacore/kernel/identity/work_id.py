
from dataclasses import dataclass

from .identifier import Identifier


@dataclass(frozen=True, eq=False, repr=False)
class WorkId(Identifier):
    """
    Strongly typed identifier for a Novacore Work unit.
    """
    pass
