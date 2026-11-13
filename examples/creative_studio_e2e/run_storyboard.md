"""Run one real Google ADK-backed Creative Studio storyboard workflow.

Requires GOOGLE_API_KEY (Google AI Studio) or supported Vertex AI credentials.
This example uses in-memory workflow storage and ADK sessions only.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone

from google.adk.agents import Agent

from novacore.google_adk import GoogleADKAgentExecutor, GoogleADKConfig
from novacore.kernel.capability import Capability
from novacore.kernel.identity import (
    ActivityId, AssignmentId, CapabilityId, ContextId, ContractId,
    ExecutionId, ObjectiveId, PlanningId, RequestId, WorkId, WorkerId,
)
from novacore.kernel.worker import Worker
from novacore.runtime.services import (
    CreateStoryboardWorkflow, StoryboardWorkflowIds, StoryboardWorkflowService,
)


class DemoWorkerDirectory:
    def __init__(self, worker: Worker) -> None:
        self.worker = worker

    def find_workers_with_capabilities(self, required_capability_ids):
        if required_capability_ids.issubset(set(self.worker.capability_ids)):
            return (self.worker,)
        return ()

    def get_capabilities(self, capability_ids):
        return tuple(
            Capability(item, "storyboard_generation", "Generate storyboard shot packages")
            for item in capability_ids
        )


class DemoWorkflowStore:
    """Demonstration-only in-memory implementation of the Runtime store port."""
    def __init__(self) -> None:
        self.records = []

    def save_initial_workflow(self, **records) -> None:
        self.records.append(("initial", records))

    def save_execution(self, execution) -> None:
        self.records.append(("execution", execution))


def main() -> None:
    capability_id = CapabilityId("storyboard-generation")
    worker = Worker(WorkerId("creative-agent-01"), (capability_id,))

    agent = Agent(
        name="storyboard_shot_agent",
        model=os.getenv("NOVACORE_GEMINI_MODEL", "gemini-flash-latest"),
        description="Creates production-ready cinematic storyboard shot packages.",
        instruction=(
            "You are a professional cinematic storyboard artist. Create exactly one "
            "storyboard shot package from the user's JSON input. Return a concise, "
            "well-structured response with: shot title, duration, character, setting, "
            "action, expression, camera angle, camera movement, lens, lighting, "
            "visual ambiance, audio ambiance, dialogue, and 9:16 composition. "
            "Do not invent character identity details not supplied in the input."
        ),
    )
    executor = GoogleADKAgentExecutor.from_agent(
        agent=agent,
        config=GoogleADKConfig(app_name="novacore_creative_studio"),
    )

    store = DemoWorkflowStore()
    service = StoryboardWorkflowService(
        store=store,
        workers=DemoWorkerDirectory(worker),
        agent_executor=executor,
    )
    command = CreateStoryboardWorkflow(
        ids=StoryboardWorkflowIds(
            request_id=RequestId("request-demo-001"),
            context_id=ContextId("context-demo-001"),
            objective_id=ObjectiveId("objective-demo-001"),
            activity_id=ActivityId("activity-demo-001"),
            planning_id=PlanningId("planning-demo-001"),
            work_id=WorkId("work-demo-001"),
            contract_ids=(ContractId("contract-demo-001"),),
            assignment_id=AssignmentId("assignment-demo-001"),
            execution_id=ExecutionId("execution-demo-001"),
        ),
        request_description="Create the opening shot for a science-fiction comedy reel.",
        objective_description="Establish the protagonist and the time-travel premise.",
        planning_description="Generate one visually clear opening storyboard shot.",
        work_description="Create storyboard shot 01.",
        contract_descriptions=("Include all required cinematic production fields.",),
        context_attributes={"episode": 1, "shot_number": 1, "format": "vertical_reel"},
        required_capability_ids=frozenset({capability_id}),
        execution_input={
            "shot_number": 1,
            "duration_seconds": 8,
            "character": "Nana, the established protagonist",
            "character_reference": "Preserve the supplied master character identity.",
            "setting": "A modern home office with three monitors",
            "action": "One monitor flickers with an impossible time anomaly.",
            "tone": "Playful science-fiction comedy, not dark",
            "aspect_ratio": "9:16",
        },
        created_at=datetime.now(timezone.utc),
    )

    result = service.create_and_execute(command)
    print("\n=== GOOGLE ADK STORYBOARD RESULT ===\n")
    print(result.agent_result.output.get("text", ""))
    print("\n=== NOVACORE EXECUTION ===")
    print(f"Activity: {result.activity.id}")
    print(f"Assignment: {result.assignment.id}")
    print(f"Execution: {result.execution.id}")
    print(f"Persisted records: {len(store.records)} store operations")


if __name__ == "__main__":
    main()

