from novacore.kernel.identity import ContractId, WorkId
from novacore.kernel.contract import Contract

contract = Contract(
    id=ContractId("contract-001"),
    work_id=WorkId("work-001"),
    description=(
        "Deliver a competitor research report covering "
        "five competitors, their positioning, and pricing."
    ),
)
