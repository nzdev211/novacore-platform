
from types import MappingProxyType

import pytest

from novacore.kernel.context import ContextAttributes


def test_context_attributes_creation():
    attributes = ContextAttributes(
        values={
            "title": "Creative Studio",
            "language": "English",
        }
    )

    assert attributes.values["title"] == "Creative Studio"
    assert attributes.values["language"] == "English"


def test_context_attributes_accepts_nested_mapping():
    attributes = ContextAttributes(
        values={
            "settings": {
                "language": "English",
                "temperature": 0.7,
            }
        }
    )

    assert attributes.values["settings"]["language"] == "English"


def test_context_attributes_converts_list_to_tuple():
    attributes = ContextAttributes(
        values={"tags": ["research", "writing"]}
    )

    assert attributes.values["tags"] == ("research", "writing")


def test_context_attributes_converts_set_to_frozenset():
    attributes = ContextAttributes(
        values={"tags": {"research", "writing"}}
    )

    assert isinstance(attributes.values["tags"], frozenset)


def test_context_attributes_nested_mapping_is_immutable():
    attributes = ContextAttributes(
        values={"settings": {"language": "English"}}
    )

    assert isinstance(attributes.values, MappingProxyType)
    assert isinstance(attributes.values["settings"], MappingProxyType)

    with pytest.raises(TypeError):
        attributes.values["settings"]["language"] = "Indonesian"


def test_context_attributes_rejects_non_mapping():
    with pytest.raises(TypeError):
        ContextAttributes(values=["invalid"])


def test_context_attributes_rejects_empty_key():
    with pytest.raises(ValueError):
        ContextAttributes(values={"": "value"})


def test_context_attributes_rejects_whitespace_key():
    with pytest.raises(ValueError):
        ContextAttributes(values={"   ": "value"})


def test_context_attributes_rejects_unsupported_object():
    with pytest.raises(TypeError):
        ContextAttributes(values={"resource": object()})


def test_context_attributes_rejects_circular_reference():
    values = {}
    values["self"] = values

    with pytest.raises(ValueError):
        ContextAttributes(values=values)


def test_context_attributes_equality():
    first = ContextAttributes(
        values={"title": "Creative Studio", "version": 1}
    )

    second = ContextAttributes(
        values={"version": 1, "title": "Creative Studio"}
    )

    assert first == second


def test_context_attributes_hash():
    first = ContextAttributes(values={"title": "Creative Studio"})
    second = ContextAttributes(values={"title": "Creative Studio"})

    assert hash(first) == hash(second)

