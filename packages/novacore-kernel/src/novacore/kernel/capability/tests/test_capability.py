
from dataclasses import FrozenInstanceError

import pytest

from novacore.kernel.capability import Capability
from novacore.kernel.identity import CapabilityId, WorkId


def create_capability(
    capability_id: str = "capability-001",
    name: str = "Research",
    description: str = "Research information.",
) -> Capability:
    return Capability(
        id=CapabilityId(capability_id),
        name=name,
        description=description,
    )


def test_capability_creation():
    capability = create_capability()

    assert capability.id == CapabilityId("capability-001")
    assert capability.name == "Research"
    assert capability.description == "Research information."


def test_capability_requires_capability_id():
    with pytest.raises(TypeError):
        Capability(
            id=WorkId("work-001"),
            name="Research",
            description="Research information.",
        )


def test_capability_rejects_non_string_name():
    with pytest.raises(TypeError):
        Capability(
            id=CapabilityId("capability-001"),
            name=123,
            description="Research information.",
        )


def test_capability_rejects_empty_name():
    with pytest.raises(ValueError):
        create_capability(name="")


def test_capability_rejects_whitespace_name():
    with pytest.raises(ValueError):
        create_capability(name="   ")


def test_capability_rejects_non_string_description():
    with pytest.raises(TypeError):
        Capability(
            id=CapabilityId("capability-001"),
            name="Research",
            description=123,
        )


def test_capability_rejects_empty_description():
    with pytest.raises(ValueError):
        create_capability(description="")


def test_capability_rejects_whitespace_description():
    with pytest.raises(ValueError):
        create_capability(description="   ")


def test_capability_is_immutable():
    capability = create_capability()

    with pytest.raises(FrozenInstanceError):
        capability.name = "Writing"


def test_capability_equality_uses_identity():
    first = create_capability(
        capability_id="capability-001",
        name="Research",
    )

    second = create_capability(
        capability_id="capability-001",
        name="Different name",
    )

    assert first == second


def test_capabilities_with_different_ids_are_not_equal():
    first = create_capability(capability_id="capability-001")
    second = create_capability(capability_id="capability-002")

    assert first != second


def test_capability_hash_uses_identity():
    first = create_capability(capability_id="capability-001")
    second = create_capability(capability_id="capability-001")

    assert hash(first) == hash(second)


def test_capability_preserves_original_name():
    capability = create_capability(name="  Research  ")

    assert capability.name == "  Research  "
