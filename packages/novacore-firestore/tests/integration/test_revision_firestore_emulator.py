"""Real Firestore Emulator coverage for the revision persistence adapters.

Run with FIRESTORE_EMULATOR_HOST set and google-cloud-firestore installed.
The tests use unique document IDs and remove their own records afterward.
"""
from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from uuid import uuid4

import pytest

pytestmark = pytest.mark.skipif(
    not os.getenv("FIRESTORE_EMULATOR_HOST"),
    reason="Set FIRESTORE_EMULATOR_HOST to run Firestore Emulator revision tests.",
)

firestore = pytest.importorskip("google.cloud.firestore")

from novacore.firestore import FirestoreReviewStore, FirestoreWorkflowStore
from novacore.firestore.revision_review_creator import StoreRevisionReviewCreator
from novacore.firestore.revision_source_store import FirestoreRevisionSourceStore
from novacore.firestore.revision_store import (
    FirestoreRevisionRecordStore, RevisionReservationConflict,
)
from novacore.kernel.activity import Activity, ActivityStatus
from novacore.kernel.assignment import Assignment
from novacore.kernel.context import Context, ContextAttributes
from novacore.kernel.contract import Contract
from novacore.kernel.execution import Execution
from novacore.kernel.identity import (
    ActivityId, AssignmentId, ContextId, ContractId, ExecutionId,
    ObjectiveId, PlanningId, RequestId, WorkId, WorkerId,
)
from novacore.kernel.objective import Objective
from novacore.kernel.planning import Planning
from novacore.kernel.request import Request
from novacore.kernel.work import Work
from novacore.runtime.ports import (
    ExecutionRecord, ExecutionStatus, ReviewRecord, ReviewStatus, RevisionResult,
)


def _client():
    return firestore.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT", "novacore-firestore-test"))


def _cleanup(client, refs):
    for ref in refs:
        try:
            ref.delete()
        except Exception:
            pass


def test_revision_reservation_is_atomic_and_completed_result_replays():
    client = _client()
    token = uuid4().hex
    source_review_id = f"source-review-{token}"
    key = f"revision-key-{token}"
    store = FirestoreRevisionRecordStore(client=client)
    ref = store._ref(source_review_id, key)

    def reserve():
        try:
            return store.reserve_revision(source_review_id=source_review_id, idempotency_key=key)
        except RevisionReservationConflict:
            return "conflict"

    try:
        with ThreadPoolExecutor(max_workers=8) as pool:
            outcomes = list(pool.map(lambda _: reserve(), range(8)))
        assert sum(item is None for item in outcomes) == 1
        assert outcomes.count("conflict") == 7

        result = RevisionResult(
            source_review_id=source_review_id,
            activity_id=f"activity-{token}",
            work_id=f"work-{token}",
            execution_id=f"execution-{token}",
            review_id=f"review-{token}",
        )
        store.complete_revision(
            source_review_id=source_review_id, idempotency_key=key, result=result,
        )
        replay = store.reserve_revision(source_review_id=source_review_id, idempotency_key=key)
        assert replay is not None
        assert replay.execution_id == result.execution_id
        assert replay.review_id == result.review_id
    finally:
        _cleanup(client, [ref])


def test_firestore_revision_source_and_pending_review_creator_round_trip():
    client = _client()
    token = uuid4().hex
    now = datetime.now(timezone.utc)

    request = Request(RequestId(f"req-{token}"), "Create a storyboard shot")
    context = Context(ContextId(f"ctx-{token}"), ContextAttributes({"studio": "test"}))
    objective = Objective(ObjectiveId(f"obj-{token}"), "Revise the lighting")
    activity = Activity(
        ActivityId(f"act-{token}"), context.id, ActivityStatus.ACTIVE,
        now, now, request.id, objective.id,
    )
    planning = Planning(PlanningId(f"plan-{token}"), activity.id, objective.id, "Lighting pass")
    work = Work(WorkId(f"work-{token}"), activity.id, "Storyboard shot", planning.id)
    contract = Contract(ContractId(f"contract-{token}"), work.id, "Produce one shot")
    assignment = Assignment(
        AssignmentId(f"assignment-{token}"), work.id, WorkerId(f"worker-{token}"),
    )
    execution = Execution(ExecutionId(f"execution-{token}"), assignment.id)

    workflow_store = FirestoreWorkflowStore(client=client)
    review_store = FirestoreReviewStore(client=client)
    workflow_store.save_initial_workflow(
        request=request, context=context, objective=objective, activity=activity,
        planning=planning, work=work, contracts=(contract,), assignment=assignment,
    )
    workflow_store.save_execution(execution)
    workflow_store.transition_execution(
        ExecutionRecord(execution.id, assignment.id, ExecutionStatus.RUNNING, now),
        expected_status=None,
    )
    workflow_store.transition_execution(
        ExecutionRecord(
            execution.id, assignment.id, ExecutionStatus.SUCCEEDED, now,
            output={"shot_spec": {"camera": "wide", "lighting": "cool"}},
        ),
        expected_status=ExecutionStatus.RUNNING,
    )
    source_review = ReviewRecord(
        review_id=f"source-review-{token}", activity_id=activity.id, work_id=work.id,
        execution_id=execution.id, status=ReviewStatus.PENDING,
        created_at=now, updated_at=now,
    )
    review_store.create_review(source_review)
    review_store.transition_review(
        ReviewRecord(
            review_id=source_review.review_id, activity_id=activity.id, work_id=work.id,
            execution_id=execution.id, status=ReviewStatus.CHANGES_REQUESTED,
            created_at=now, updated_at=now, reviewer_id="reviewer-test",
            feedback="Make the lighting warmer",
        ),
        expected_status=ReviewStatus.PENDING,
    )

    source_loader_calls = []
    source_store = FirestoreRevisionSourceStore(
        review_store=review_store,
        workflow_store=workflow_store,
        authorize=lambda creator, activity_id, work_id: creator == "creator-test",
        load_execution_input=lambda activity_id, execution_id: (
            source_loader_calls.append((activity_id, execution_id))
            or {"brief": "A scientist discovers a time portal"}
        ),
    )
    source = source_store.load_revision_source(
        review_id=source_review.review_id, creator_id="creator-test",
    )
    assert source is not None
    assert source.execution_id == execution.id.value
    assert source.review_status == "CHANGES_REQUESTED"
    assert source.execution_output["shot_spec"]["camera"] == "wide"
    assert source.execution_input["brief"] == "A scientist discovers a time portal"
    assert source_loader_calls == [(activity.id.value, execution.id.value)]
    assert source_store.load_revision_source(
        review_id=source_review.review_id, creator_id="not-authorized",
    ) is None

    creator = StoreRevisionReviewCreator(
        review_store=review_store,
        create_review_id=lambda: f"new-review-{token}",
        clock=lambda: now,
    )
    new_review_id = creator.create_pending_review(
        activity_id=activity.id.value,
        work_id=work.id.value,
        execution_id=f"new-execution-{token}",
        source_review_id=source_review.review_id,
        creator_id="creator-test",
    )
    new_review = review_store.load_review(new_review_id)
    assert new_review is not None
    assert new_review.status is ReviewStatus.PENDING
    assert new_review.execution_id.value == f"new-execution-{token}"

    # Clean up the test's uniquely named documents from each collection.
    from novacore.firestore.workflow_store import _document_id
    from novacore.firestore.review_store import _doc_id
    refs = [
        client.collection("requests").document(_document_id(request.id)),
        client.collection("contexts").document(_document_id(context.id)),
        client.collection("objectives").document(_document_id(objective.id)),
        client.collection("activities").document(_document_id(activity.id)),
        client.collection("plannings").document(_document_id(planning.id)),
        client.collection("works").document(_document_id(work.id)),
        client.collection("contracts").document(_document_id(contract.id)),
        client.collection("assignments").document(_document_id(assignment.id)),
        client.collection("executions").document(_document_id(execution.id)),
        client.collection("execution_lifecycle").document(_document_id(execution.id)),
        client.collection("human_reviews").document(_doc_id(source_review.review_id)),
        client.collection("human_reviews").document(_doc_id(new_review_id)),
    ]
    _cleanup(client, refs)

