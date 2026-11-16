"""Opt-in live Google ADK + Firestore Emulator revision workflow test.

This test makes a real Gemini API request and writes to the configured Firestore
Emulator. It is skipped during ordinary test runs unless all explicit opt-ins
and credentials are present.
"""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

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
        "FIRESTORE_EMULATOR_HOST to run the live Google ADK + Firestore test."
    ),
)


def test_revision_api_invokes_live_google_adk_and_persists_pending_review():
    """Exercise API -> Runtime -> Firestore -> real ADK -> Firestore review."""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from google.auth.credentials import AnonymousCredentials
    from google.cloud import firestore
    from google.adk.agents import Agent

    from novacore.fastapi import create_revision_service_router
    from novacore.firestore import (
        FirestoreReviewStore,
        FirestoreRevisionRecordStore,
        FirestoreRevisionSourceStore,
        FirestoreWorkflowStore,
        StoreRevisionReviewCreator,
    )
    from novacore.google_adk import GoogleADKAgentExecutor, GoogleADKConfig
    from novacore.kernel.activity import Activity, ActivityStatus
    from novacore.kernel.assignment import Assignment
    from novacore.kernel.context import Context, ContextAttributes
    from novacore.kernel.contract import Contract
    from novacore.kernel.execution import Execution
    from novacore.kernel.identity import (
        ActivityId, AssignmentId, ContextId, ContractId, ExecutionId,
        ObjectiveId, PlanningId, RequestId, WorkerId, WorkId,
    )
    from novacore.kernel.objective import Objective
    from novacore.kernel.planning import Planning
    from novacore.kernel.request import Request
    from novacore.kernel.work import Work
    from novacore.runtime.ports import (
        ExecutionRecord, ExecutionStatus, ReviewRecord, ReviewStatus,
    )
    from novacore.runtime.services import (
        AgentRevisionExecutionPort, RevisionWorkflowService,
    )

    token = uuid.uuid4().hex
    now = datetime.now(timezone.utc)
    project = os.getenv("GOOGLE_CLOUD_PROJECT", "novacore-phase35-emulator")
    client = firestore.Client(project=project, credentials=AnonymousCredentials())

    # Every ID is unique per run; IDs are supplied by this host test harness.
    request_id = RequestId(f"p35-request-{token}")
    context_id = ContextId(f"p35-context-{token}")
    objective_id = ObjectiveId(f"p35-objective-{token}")
    activity_id = ActivityId(f"p35-activity-{token}")
    planning_id = PlanningId(f"p35-planning-{token}")
    work_id = WorkId(f"p35-work-{token}")
    contract_id = ContractId(f"p35-contract-{token}")
    worker_id = WorkerId(f"p35-worker-{token}")
    assignment_id = AssignmentId(f"p35-assignment-{token}")
    original_execution_id = ExecutionId(f"p35-original-execution-{token}")
    source_review_id = f"p35-source-review-{token}"
    creator_id = f"p35-creator-{token}"

    workflow_store = FirestoreWorkflowStore(client)
    review_store = FirestoreReviewStore(client)
    revision_store = FirestoreRevisionRecordStore(client)

    request = Request(request_id, "Create a concise cinematic storyboard shot.")
    context = Context(context_id, ContextAttributes({"project": "phase35-live-test"}))
    objective = Objective(objective_id, "Produce a revised storyboard shot description.")
    activity = Activity(
        id=activity_id, context_id=context_id, status=ActivityStatus.ACTIVE,
        created_at=now, updated_at=now, request_id=request_id,
        objective_id=objective_id,
    )
    planning = Planning(planning_id, activity_id, objective_id, "Revise the shot using reviewer feedback.")
    work = Work(work_id, activity_id, "Storyboard shot revision", planning_id)
    contract = Contract(contract_id, work_id, "Return one improved shot description.")
    assignment = Assignment(assignment_id, work_id, worker_id)

    workflow_store.save_initial_workflow(
        request=request, context=context, objective=objective, activity=activity,
        planning=planning, work=work, contracts=(contract,), assignment=assignment,
    )
    original_execution = Execution(original_execution_id, assignment_id)
    workflow_store.save_execution(original_execution)
    workflow_store.transition_execution(
        ExecutionRecord(original_execution_id, assignment_id, ExecutionStatus.PENDING, now),
        expected_status=None,
    )
    workflow_store.transition_execution(
        ExecutionRecord(original_execution_id, assignment_id, ExecutionStatus.RUNNING, now),
        expected_status=ExecutionStatus.PENDING,
    )
    workflow_store.transition_execution(
        ExecutionRecord(
            original_execution_id, assignment_id, ExecutionStatus.SUCCEEDED, now,
            output={"text": "A character enters a dimly lit room."},
            metadata={"provider": "seeded-test-execution"},
        ),
        expected_status=ExecutionStatus.RUNNING,
    )

    # A real persisted review is moved from PENDING to CHANGES_REQUESTED.
    review_store.create_review(ReviewRecord(
        review_id=source_review_id, activity_id=activity_id, work_id=work_id,
        execution_id=original_execution_id, status=ReviewStatus.PENDING,
        created_at=now, updated_at=now,
    ))
    review_store.transition_review(ReviewRecord(
        review_id=source_review_id, activity_id=activity_id, work_id=work_id,
        execution_id=original_execution_id, status=ReviewStatus.CHANGES_REQUESTED,
        created_at=now, updated_at=now, reviewer_id="phase35-reviewer",
        feedback="Make the lighting warmer and the character's action clearer.",
    ), expected_status=ReviewStatus.PENDING)

    source_store = FirestoreRevisionSourceStore(
        review_store=review_store,
        workflow_store=workflow_store,
        authorize=lambda user, activity, work: (
            user == creator_id and activity == activity_id.value and work == work_id.value
        ),
        load_execution_input=lambda activity, execution: {
            "task": "Improve the original storyboard shot description.",
            "source_activity": activity,
            "source_execution": execution,
        },
    )

    model = os.getenv("NOVACORE_ADK_MODEL", "gemini-2.5-flash")
    live_agent = Agent(
        name="phase35_revision_test_agent",
        model=model,
        instruction=(
            "You are a deterministic integration-test agent. Read the supplied "
            "revision context and respond with exactly the token "
            "PHASE35_LIVE_ADK_OK. Do not add any other words."
        ),
    )
    agent_executor = GoogleADKAgentExecutor.from_agent(
        agent=live_agent,
        config=GoogleADKConfig(
            app_name=f"novacore-phase35-{token}", session_backend="memory"
        ),
    )

    execution_ids = iter([ExecutionId(f"p35-revised-execution-{token}")])
    review_ids = iter([f"p35-revised-review-{token}"])
    execution_port = AgentRevisionExecutionPort(
        workflow_store=workflow_store,
        agent_executor=agent_executor,
        create_execution_id=lambda: next(execution_ids),
    )
    review_creator = StoreRevisionReviewCreator(
        review_store=review_store,
        create_review_id=lambda: next(review_ids),
    )
    service = RevisionWorkflowService(
        source_store=source_store,
        execution_port=execution_port,
        revision_store=revision_store,
        review_creator=review_creator,
    )

    app = FastAPI()
    app.include_router(create_revision_service_router(
        revision_service=service,
        authenticate_creator=lambda: creator_id,
    ))

    idempotency_key = f"p35-idempotency-{token}"
    with TestClient(app) as http:
        response = http.post(
            f"/reviews/{source_review_id}/revisions",
            json={
                "additional_instructions": "Apply the requested warmer lighting.",
                "idempotency_key": idempotency_key,
            },
        )
        assert response.status_code == 202, response.text
        first = response.json()
        assert first["status"] == "PENDING"
        assert first["execution_id"] == f"p35-revised-execution-{token}"

        persisted_execution = workflow_store.load_execution(ExecutionId(first["execution_id"]))
        assert persisted_execution is not None
        assert persisted_execution.status is ExecutionStatus.SUCCEEDED
        assert persisted_execution.metadata["provider"] == "google-adk"
        assert "PHASE35_LIVE_ADK_OK" in persisted_execution.output["text"]

        pending_review = review_store.load_review(first["review_id"])
        assert pending_review is not None
        assert pending_review.status is ReviewStatus.PENDING
        assert pending_review.execution_id == ExecutionId(first["execution_id"])

        # Same key must replay the stored result without a second ADK execution.
        replay = http.post(
            f"/reviews/{source_review_id}/revisions",
            json={
                "additional_instructions": "Apply the requested warmer lighting.",
                "idempotency_key": idempotency_key,
            },
        )
        assert replay.status_code == 202, replay.text
        second = replay.json()
        assert second["replayed"] is True
        assert second["execution_id"] == first["execution_id"]
        assert second["review_id"] == first["review_id"]

