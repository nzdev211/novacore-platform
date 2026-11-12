
from dataclasses import dataclass

from .identifier import Identifier


@dataclass(frozen=True, eq=False, repr=False)
class WorkerId(Identifier):
    """
    Strongly typed identifier for a Novacore Worker.

    Identifies an execution resource independently of
    its implementation type.
    """
    pass

