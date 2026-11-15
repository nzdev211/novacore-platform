from novacore.runtime.ports.revision_execution import CallbackRevisionExecutionPort
from novacore.runtime.ports.revision_workflow import RevisionSource


def test_callback_port_delegates_to_host_runtime_and_returns_execution():
    calls = []
    def execute(source, instructions, key):
        calls.append((source.execution_id, instructions, key))
        return "execution-2", "succeeded", {"shot": "revised"}

    port = CallbackRevisionExecutionPort(execute)
    source = RevisionSource(
        review_id="review-1", activity_id="activity-1", work_id="work-1",
        execution_id="execution-1", review_status="CHANGES_REQUESTED",
        review_feedback="Improve the framing", execution_input={"brief": "scene"},
        execution_output={"shot": "original"},
    )
    result = port.execute_revision(
        source=source, additional_instructions="Use a close-up", idempotency_key="rev-key-1",
    )
    assert result.execution_id == "execution-2"
    assert result.execution_status == "succeeded"
    assert result.output == {"shot": "revised"}
    assert calls == [("execution-1", "Use a close-up", "rev-key-1")]

