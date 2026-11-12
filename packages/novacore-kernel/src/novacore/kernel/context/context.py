
from dataclasses import dataclass

from novacore.kernel.identity import ContextId

from .context_attributes import ContextAttributes


@dataclass(frozen=True, eq=False)
class Context:
    """
    Represents a contextual environment within Novacore.

    Context provides identity and structured contextual attributes.
    """

    id: ContextId
    attributes: ContextAttributes

    def __post_init__(self) -> None:
        if not isinstance(self.id, ContextId):
            raise TypeError(
                "Context id must be a ContextId."
            )

        if not isinstance(self.attributes, ContextAttributes):
            raise TypeError(
                "Context attributes must be ContextAttributes."
            )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Context):
            return NotImplemented

        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

