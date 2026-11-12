from dataclasses import dataclass
from .identifier import Identifier


@dataclass(frozen=True, eq=False, repr=False)
class ContextId(Identifier):
    pass