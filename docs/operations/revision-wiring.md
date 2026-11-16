# Operating the Phase 34 Revision Workflow

## Composition

The host application owns the composition root and supplies:

- one synchronous Firestore client for Novacore Firestore stores;
- an `AgentExecutor`, such as a configured `GoogleADKAgentExecutor`;
- an execution-ID factory returning a new `ExecutionId`;
- a review-ID factory returning a unique string;
- creator authentication and resource-level authorization;
- a loader for the exact original execution input.

Illustrative wiring:

```python
from fastapi import FastAPI
from google.cloud import firestore

from novacore.fastapi import create_revision_service_router
from novacore.firestore import (
    FirestoreReviewStore,
    FirestoreRevisionRecordStore,
    FirestoreRevisionSourceStore,
    FirestoreWorkflowStore,
    StoreRevisionReviewCreator,
)
from novacore.google_adk import GoogleADKAgentExecutor, GoogleADKConfig
from novacore.kernel.identity import ExecutionId
from novacore.runtime.services import AgentRevisionExecutionPort, RevisionWorkflowService

client = firestore.Client()
workflow_store = FirestoreWorkflowStore(client)
review_store = FirestoreReviewStore(client)
revision_store = FirestoreRevisionRecordStore(client)

# Construct your ADK agent and configure credentials/session storage separately.
agent_executor = GoogleADKAgentExecutor.from_agent(
    agent=storyboard_agent,
    config=GoogleADKConfig(app_name="creative-studio", session_backend="memory"),
)

source_store = FirestoreRevisionSourceStore(
    review_store=review_store,
    workflow_store=workflow_store,
    authorize=lambda creator_id, activity_id, work_id: app_authorize_revision(
        creator_id, activity_id, work_id
    ),
    load_execution_input=lambda activity_id, execution_id: load_saved_agent_input(
        activity_id, execution_id
    ),
)
execution_port = AgentRevisionExecutionPort(
    workflow_store=workflow_store,
    agent_executor=agent_executor,
    create_execution_id=lambda: ExecutionId(id_service.new_id()),
)
review_creator = StoreRevisionReviewCreator(
    review_store=review_store,
    create_review_id=lambda: id_service.new_id(),
)
revision_service = RevisionWorkflowService(
    source_store=source_store,
    execution_port=execution_port,
    revision_store=revision_store,
    review_creator=review_creator,
)

app = FastAPI()
app.include_router(
    create_revision_service_router(
        revision_service=revision_service,
        authenticate_creator=current_authenticated_creator_id,
    )
)
```

The names `storyboard_agent`, `app_authorize_revision`, `load_saved_agent_input`, `id_service`, and `current_authenticated_creator_id` are host-application placeholders, not Novacore APIs.

## Required host safeguards

1. Ensure `create_execution_id` and `create_review_id` return unique, stable IDs.
2. Ensure authorization is checked against the exact Activity and Work before loading or executing a revision.
3. Keep the execution-input loader bound to the exact reviewed execution; never load a newer execution by “latest” ordering.
4. Configure provider credentials and ADK session persistence for the deployment environment.
5. Treat a reserved revision key after an uncertain execution as an operator-reconciliation task. Do not delete it to make a retry work.
6. Protect the API with authentication, tenant isolation, CSRF controls where applicable, and resource-level authorization.

## Validation

Run Runtime and Firestore unit/integration tests with the package source directories on `PYTHONPATH`. Run the Firestore Emulator test separately with `FIRESTORE_EMULATOR_HOST` configured. A passing fake AgentExecutor test proves Runtime wiring and lifecycle sequencing, not live Google ADK execution or production Firestore behavior.

