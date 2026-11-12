from dataclasses import dataclass

from novacore.kernel.identity import RequestId


@dataclass(frozen=True, eq=False)
class Request:
    """Represents an incoming request."""

    id: RequestId
    description: str

    def __post_init__(self) -> None:
        if not isinstance(self.id, RequestId):
            raise TypeError("Request id must be a RequestId.")

        if not isinstance(self.description, str):
            raise TypeError("Request description must be a string.")

        if not self.description.strip():
            raise ValueError(
                "Request description cannot be empty or whitespace-only."
            )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Request):
            return NotImplemented

        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
