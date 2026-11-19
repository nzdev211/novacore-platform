from novacore_server.api import ApiDependencies


def test_api_dependencies_are_optional_and_host_supplied():
    deps = ApiDependencies(authenticate_reviewer=lambda: "r1")
    assert deps.authenticate_reviewer() == "r1"
    assert deps.authenticate_creator is None
    assert deps.load_review_context is None
