from novacore_server.container import load_factory


def test_load_factory_resolves_callable():
    factory = load_factory("json:loads")
    assert factory('{"ok": true}') == {"ok": True}


def test_load_factory_rejects_invalid_path():
    import pytest
    with pytest.raises(ValueError):
        load_factory("json.loads")


def test_load_factory_rejects_non_callable():
    import pytest
    with pytest.raises(TypeError):
        load_factory("json:__doc__")

