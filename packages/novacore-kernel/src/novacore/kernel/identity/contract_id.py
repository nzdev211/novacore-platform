
from dataclasses import dataclass

from .identifier import Identifier


@dataclass(frozen=True, eq=False, repr=False)
class ContractId(Identifier):
    """
    Strongly typed identifier for a Novacore Contract.
    """
    pass

