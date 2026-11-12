import pytest

from novacore.kernel.identity import ObjectiveId
from novacore.kernel.objective import Objective


def test_objective_creation_and_identity_equality():
    first = Objective(ObjectiveId("objective-1"), "Increase awareness")
    same_identity = Objective(ObjectiveId("objective-1"), "Different description")
    assert first == same_identity
    assert hash(first) == hash(same_identity)


@pytest.mark.parametrize("value", ["", "   "])
def test_objective_rejects_empty_description(value):
    with pytest.raises(ValueError):
        Objective(ObjectiveId("objective-1"), value)


def test_objective_rejects_wrong_types():
    with pytest.raises(TypeError):
        Objective("objective-1", "Increase awareness")
    with pytest.raises(TypeError):
        Objective(ObjectiveId("objective-1"), None)

