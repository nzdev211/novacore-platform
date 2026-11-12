import pytest

from novacore.kernel.identity import RequestId
from novacore.kernel.request import Request


def test_request_creation_and_preserves_description():
    request = Request(RequestId("request-1"), "  Create a campaign  ")
    assert request.description == "  Create a campaign  "


@pytest.mark.parametrize("value", ["", "   ", "\t"])
def test_request_rejects_empty_description(value):
    with pytest.raises(ValueError):
        Request(RequestId("request-1"), value)


def test_request_rejects_wrong_types():
    with pytest.raises(TypeError):
        Request("request-1", "Create a campaign")
    with pytest.raises(TypeError):
        Request(RequestId("request-1"), 123)


def test_request_is_immutable_and_identity_based():
    first = Request(RequestId("request-1"), "First")
    same_identity = Request(RequestId("request-1"), "Different")
    assert first == same_identity
    assert hash(first) == hash(same_identity)
    with pytest.raises((AttributeError, TypeError)):
        first.description = "Changed"

