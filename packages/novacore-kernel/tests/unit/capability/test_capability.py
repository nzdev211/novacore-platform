import pytest

from novacore.kernel.capability import Capability
from novacore.kernel.identity import CapabilityId


def make_capability(**overrides):
    values = {
        "id": CapabilityId("capability-1"),
        "name": "Research",
        "description": "Research and synthesize information",
    }
    values.update(overrides)
    return Capability(**values)


def test_capability_creation():
    capability = make_capability()
    assert capability.name == "Research"


@pytest.mark.parametrize("value", ["", "   ", "\t"])
@pytest.mark.parametrize("field", ["name", "description"])
def test_capability_rejects_empty_required_strings(field, value):
    with pytest.raises(ValueError):
        make_capability(**{field: value})


def test_capability_rejects_wrong_types():
    with pytest.raises(TypeError):
        make_capability(id="capability-1")
    with pytest.raises(TypeError):
        make_capability(name=123)
    with pytest.raises(TypeError):
        make_capability(description=123)


def test_capability_is_immutable_and_identity_based():
    first = make_capability()
    same_identity = make_capability(name="Writing", description="Different")
    assert first == same_identity
    assert hash(first) == hash(same_identity)
    with pytest.raises((AttributeError, TypeError)):
        first.name = "Changed"

