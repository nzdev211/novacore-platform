
from dataclasses import dataclass

from .identifier import Identifier


@dataclass(frozen=True, eq=False, repr=False)
class CapabilityId(Identifier):
    """
    Strongly typed identifier for a Novacore Capability.
    """
    pass
