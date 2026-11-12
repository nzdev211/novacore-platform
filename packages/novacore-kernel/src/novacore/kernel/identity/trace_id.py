
from dataclasses import dataclass

from .identifier import Identifier


@dataclass(frozen=True, eq=False, repr=False)
class TraceId(Identifier):
    """
    Strongly typed identifier for a Novacore distributed trace.
    """
    pass

