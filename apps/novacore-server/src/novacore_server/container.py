"""Composition root: construct adapters and inject them into Runtime services.

This module belongs to the server application. Kernel and Runtime do not
construct infrastructure or import provider SDKs.
"""
from __future__ import annotations

import importlib
import uuid
from dataclasses import dataclass
from typing import Any, Callable

from .config import ServerSettings


def load_factory(path: str) -> Callable[..., Any]:
    """Load a host-supplied factory using ``package.module:callable`` syntax."""
    if not isinstance(path, str) or ":" not in path:
        raise ValueError("Factory path must use 'package.module:callable' syntax.")
    module_name, attribute = path.split(":", 1)
    if not module_name.strip() or not attribute.strip():
        raise ValueError("Factory path must use 'package.module:callable' syntax.")
    module = importlib.import_module(module_name)
    factory = getattr(module, attribute)
    if not callable(factory):
        raise TypeError(f"Configured factory {path!r} is not callable.")
    return factory


@dataclass(slots=True)
class RuntimeContainer:
    firestore_client: Any
    workflow_store: Any
    review_store: Any
    revision_record_store: Any
    human_review_service: Any
    agent_executor: Any | None = None
    revision_execution_port: Any | None = None

    def close(self) -> None:
        close = getattr(self.firestore_client, "close", None)
        if callable(close):
            close()


def build_container(
    settings: ServerSettings,
    *,
    firestore_client: Any | None = None,
    agent_factory: Callable[[ServerSettings], Any] | None = None,
    session_service: Any | None = None,
) -> RuntimeContainer:
    """Build the platform's infrastructure adapters and Runtime services.

    Firestore is shared by the workflow, review, and revision stores. The ADK
    agent itself is supplied by the host through an explicit factory; this
    avoids inventing a product-specific agent, prompt, or model configuration.
    """
    try:
        from novacore.firestore import (
            FirestoreReviewStore,
            FirestoreRevisionRecordStore,
            FirestoreWorkflowStore,
        )
        from novacore.runtime.services import HumanReviewService
    except ImportError as exc:
        raise RuntimeError(
            "Install the Novacore kernel, runtime, and Firestore packages before starting the platform server."
        ) from exc

    if firestore_client is None:
        try:
            from google.cloud import firestore
        except ImportError as exc:
            raise RuntimeError(
                "Install novacore-firestore[firestore] to initialize platform persistence."
            ) from exc
        firestore_client = firestore.Client(project=settings.firestore_project)

    workflow_store = FirestoreWorkflowStore(client=firestore_client)
    review_store = FirestoreReviewStore(client=firestore_client)
    revision_record_store = FirestoreRevisionRecordStore(client=firestore_client)
    human_review_service = HumanReviewService(review_store)

    agent_executor = None
    revision_execution_port = None
    if agent_factory is not None:
        try:
            from novacore.google_adk import GoogleADKAgentExecutor, GoogleADKConfig
            from novacore.runtime.services import AgentRevisionExecutionPort
        except ImportError as exc:
            raise RuntimeError(
                "Install novacore-google-adk[google-adk] before configuring an ADK agent."
            ) from exc
        agent = agent_factory(settings)
        adk_config = GoogleADKConfig(
            app_name=settings.google_adk_app_name,
            session_backend=settings.google_adk_session_backend,
        )
        agent_executor = GoogleADKAgentExecutor.from_agent(
            agent=agent, config=adk_config, session_service=session_service
        )
        revision_execution_port = AgentRevisionExecutionPort(
            workflow_store=workflow_store,
            agent_executor=agent_executor,
            create_execution_id=lambda: _execution_id_type()(str(uuid.uuid4())),
        )

    return RuntimeContainer(
        firestore_client=firestore_client,
        workflow_store=workflow_store,
        review_store=review_store,
        revision_record_store=revision_record_store,
        human_review_service=human_review_service,
        agent_executor=agent_executor,
        revision_execution_port=revision_execution_port,
    )


def _execution_id_type() -> Any:
    from novacore.kernel.identity import ExecutionId
    return ExecutionId

