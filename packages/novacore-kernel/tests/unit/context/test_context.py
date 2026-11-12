import pytest

from novacore.kernel.context import Context, ContextAttributes
from novacore.kernel.identity import ContextId


def test_context_creation_and_identity_equality():
    attributes = ContextAttributes({"topic": "campaign"})
    first = Context(ContextId("context-1"), attributes)
    same_identity = Context(ContextId("context-1"), ContextAttributes({"topic": "other"}))
    assert first == same_identity
    assert hash(first) == hash(same_identity)


def test_context_requires_typed_id_and_attributes():
    with pytest.raises(TypeError):
        Context("context-1", ContextAttributes({}))
    with pytest.raises(TypeError):
        Context(ContextId("context-1"), {})

