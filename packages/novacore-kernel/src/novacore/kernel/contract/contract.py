from dataclasses import dataclass

from novacore.kernel.identity import ContractId, WorkId


@dataclass(frozen=True, eq=False)
class Contract:
    """Immutable set of terms associated with a Work."""

    id: ContractId
    work_id: WorkId
    description: str

    def __post_init__(self) -> None:
        if not isinstance(self.id, ContractId):
            raise TypeError("Contract id must be a ContractId.")
        if not isinstance(self.work_id, WorkId):
            raise TypeError("Contract work_id must be a WorkId.")
        if not isinstance(self.description, str):
            raise TypeError("Contract description must be a string.")
        if not self.description.strip():
            raise ValueError("Contract description cannot be empty or whitespace-only.")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Contract):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
