import pytest

from novacore.kernel.contract import Contract
from novacore.kernel.identity import ContractId, WorkId


def make_contract(**overrides):
    values = {
        "id": ContractId("contract-1"),
        "work_id": WorkId("work-1"),
        "description": "Deliver research summary and recommendations",
    }
    values.update(overrides)
    return Contract(**values)


def test_contract_creation():
    contract = make_contract()
    assert contract.work_id == WorkId("work-1")
    assert contract.description == "Deliver research summary and recommendations"


@pytest.mark.parametrize("value", ["", "   ", "\t"])
def test_contract_rejects_empty_description(value):
    with pytest.raises(ValueError):
        make_contract(description=value)


def test_contract_rejects_wrong_types():
    with pytest.raises(TypeError):
        make_contract(id="contract-1")
    with pytest.raises(TypeError):
        make_contract(work_id="work-1")
    with pytest.raises(TypeError):
        make_contract(description=123)


def test_contract_is_immutable_and_identity_based():
    first = make_contract()
    same_identity = make_contract(description="Different terms")
    assert first == same_identity
    assert hash(first) == hash(same_identity)
    with pytest.raises((AttributeError, TypeError)):
        first.description = "Changed"


def test_multiple_contracts_can_reference_the_same_work():
    work_id = WorkId("work-1")
    first = Contract(ContractId("contract-1"), work_id, "Deliverable A")
    second = Contract(ContractId("contract-2"), work_id, "Deliverable B")
    assert first.work_id == second.work_id
    assert first.id != second.id

