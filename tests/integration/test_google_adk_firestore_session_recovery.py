"""Opt-in live ADK Firestore session persistence/recovery test.

This test makes two real Gemini calls. The second call uses a newly constructed
ADK executor and FirestoreSessionService, but the same app/user/session identity.
"""
from __future__ import annotations

import os
import uuid

import pytest

_REQUIRED = (
    os.getenv("NOVACORE_RUN_LIVE_ADK_TESTS") == "1",
    bool(os.getenv("GOOGLE_API_KEY")),
    bool(os.getenv("FIRESTORE_EMULATOR_HOST")),
)
pytestmark = pytest.mark.skipif(
    not all(_REQUIRED),
    reason=(
        "Set NOVACORE_RUN_LIVE_ADK_TESTS=1, GOOGLE_API_KEY, and "
        "FIRESTORE_EMULATOR_HOST to run live ADK Firestore session recovery."
    ),
)


def test_firestore_session_survives_executor_recreation():
    """A fresh executor resumes the same persisted ADK conversation."""
    from google.adk.agents import Agent
    from google.auth.credentials import AnonymousCredentials
    from google.cloud.firestore import AsyncClient

    from novacore.google_adk import GoogleADKAgentExecutor, GoogleADKConfig
    from novacore.kernel.identity import AssignmentId, ExecutionId, WorkerId
    from novacore.runtime.ports import AgentExecutionRequest

    token = uuid.uuid4().hex
    project = os.getenv("GOOGLE_CLOUD_PROJECT", "novacore-phase36-emulator")
    model = os.getenv("NOVACORE_ADK_MODEL", "gemini-2.5-flash")
    root_collection = f"adk-phase36-{token}"
    app_name = f"novacore-phase36-{token}"
    execution_id = ExecutionId(f"phase36-session-{token}")
    worker_id = WorkerId(f"phase36-worker-{token}")
    assignment_id = AssignmentId(f"phase36-assignment-{token}")

    # ADK's FirestoreSessionService is async; use its supported AsyncClient.
    client = AsyncClient(project=project, credentials=AnonymousCredentials())
    config = GoogleADKConfig(
        app_name=app_name,
        session_backend="firestore",
        user_id_prefix="novacore-phase36-worker",
        firestore_root_collection=root_collection,
    )
    agent = Agent(
        name="phase36_session_memory_agent",
        model=model,
        instruction=(
            "You are a session persistence test agent. Follow the user's request "
            "precisely. If asked to remember a phrase, acknowledge it briefly. "
            "If asked what phrase was previously supplied, return only that phrase."
        ),
    )

    try:
        first_executor = GoogleADKAgentExecutor.from_agent(
            agent=agent, config=config, firestore_client=client
        )
        first_result = first_executor.execute(AgentExecutionRequest(
            execution_id=execution_id,
            assignment_id=assignment_id,
            worker_id=worker_id,
            input={"message": "Remember this exact phrase for my next message: cobalt-orchid-731."},
        ))
        assert first_result.metadata["session_id"] == execution_id.value
        assert first_result.metadata["provider"] == "google-adk"

        # Simulate process/Runner recreation: do not reuse the first executor.
        second_executor = GoogleADKAgentExecutor.from_agent(
            agent=agent, config=config, firestore_client=client
        )
        second_result = second_executor.execute(AgentExecutionRequest(
            execution_id=execution_id,
            assignment_id=assignment_id,
            worker_id=worker_id,
            input={"message": "What exact phrase did I ask you to remember? Return only the phrase."},
        ))
        assert "cobalt-orchid-731" in second_result.output["text"]
        assert second_result.metadata["session_id"] == execution_id.value
    finally:
        # Keep the emulator data isolated by a unique collection per test run.
        # Deleting the collection is intentionally left to emulator cleanup tools;
        # this avoids relying on provider-specific recursive-delete behavior.
        close = getattr(client, "close", None)
        if close is not None:
            import asyncio
            asyncio.run(close())

