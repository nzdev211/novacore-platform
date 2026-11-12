
from dataclasses import dataclass

from .identifier import Identifier


@dataclass(frozen=True, eq=False, repr=False)
class RequestId(Identifier):
    """
    Strongly typed identifier for a Novacore request.
    """
    pass
