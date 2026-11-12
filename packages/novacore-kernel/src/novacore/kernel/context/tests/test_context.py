
from dataclasses import FrozenInstanceError

import pytest

from novacore.kernel.context import Context, ContextAttributes
from novacore.kernel.identity import ContextId, ActivityId


def create_context(context_id="context-001"):
    return Context(
        id=ContextId(context_id),
        attributes=ContextAttributes(
            values={
                "title": "Creative Studio",
                "language": "English",
            }
        ),
    )


def test_context_creation():
    context = create_context()

    assert context.id == ContextId("context-001")
    assert context.attributes.values["title"] == "Creative Studio"


def test_context_requires_context_id():
    with pytest.raises(TypeError):
        Context(
            id=ActivityId("activity-001"),
            attributes=ContextAttributes(values={}),
        )


def test_context_requires_context_attributes():
    with pytest.raises(TypeError):
        Context(
            id=ContextId("context-001"),
            attributes={},
        )


def test_context_is_immutable():
    context = create_context()

    with pytest.raises(FrozenInstanceError):
        context.id = ContextId("context-002")


def test_context_equality_uses_identity():
    first = create_context("context-001")
    second = create_context("context-001")

    assert first == second


def test_context_different_ids_are_not_equal():
    first = create_context("context-001")
    second = create_context("context-002")

    assert first != second


def test_context_hash_uses_identity():
    first = create_context("context-001")
    second = create_context("context-001")

    assert hash(first) == hash(second)

