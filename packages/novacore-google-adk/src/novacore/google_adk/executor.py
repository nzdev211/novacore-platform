from __future__ import annotations

import asyncio
import json
import threading
from typing import Any

from novacore.runtime.ports import AgentExecutionRequest, AgentExecutionResult
from .config import GoogleADKConfig


class GoogleADKAgentExecutor:
    """Google ADK implementation of Novacore Runtime's AgentExecutor port."""

    def __init__(self, *, runner: Any, config: GoogleADKConfig) -> None:
        if runner is None:
            raise TypeError("runner is required.")
        if not isinstance(config, GoogleADKConfig):
            raise TypeError("config must be GoogleADKConfig.")
        self._runner = runner
        self._config = config

    @classmethod
    def from_agent(cls, *, agent: Any, config: GoogleADKConfig,
                   session_service: Any | None = None) -> "GoogleADKAgentExecutor":
        if agent is None:
            raise TypeError("agent is required.")
        try:
            from google.adk.apps import App
            from google.adk.runners import Runner
            from google.adk.sessions import InMemorySessionService
        except ImportError as exc:
            raise RuntimeError("Install novacore-google-adk[google-adk].") from exc
        if session_service is None:
            if config.session_backend != "memory":
                raise ValueError("A custom session_service is required for backend='custom'.")
            session_service = InMemorySessionService()
        app = App(name=config.app_name, root_agent=agent)
        runner = Runner(app=app, session_service=session_service)
        return cls(runner=runner, config=config)

    def execute(self, request: AgentExecutionRequest) -> AgentExecutionResult:
        if not isinstance(request, AgentExecutionRequest):
            raise TypeError("request must be AgentExecutionRequest.")
        return _run_sync(self._execute_async(request))

    async def _execute_async(self, request: AgentExecutionRequest) -> AgentExecutionResult:
        from google.genai import types

        session_id = request.execution_id.value
        user_id = f"{self._config.user_id_prefix}:{request.worker_id.value}"
        service = self._runner.session_service
        session = await service.get_session(app_name=self._config.app_name,
                                            user_id=user_id, session_id=session_id)
        if session is None:
            await service.create_session(app_name=self._config.app_name,
                                         user_id=user_id, session_id=session_id)
        payload = {"execution_id": session_id,
                   "assignment_id": request.assignment_id.value,
                   "worker_id": request.worker_id.value,
                   "input": _json_safe(request.input)}
        message = types.Content(role="user", parts=[types.Part(text=json.dumps(
            payload, ensure_ascii=False, sort_keys=True))])
        events = []
        async for event in self._runner.run_async(user_id=user_id, session_id=session_id,
                                                  new_message=message):
            events.append(event)
        final_text = _last_text(events)
        return AgentExecutionResult(output={"text": final_text}, metadata={
            "provider": "google-adk", "app_name": self._config.app_name,
            "session_id": session_id, "event_count": len(events)})


def _run_sync(coroutine):
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coroutine)
    result, error = [], []
    def target():
        try:
            result.append(asyncio.run(coroutine))
        except BaseException as exc:
            error.append(exc)
    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    thread.join()
    if error:
        raise error[0]
    return result[0]


def _last_text(events: list[Any]) -> str:
    text = ""
    for event in events:
        content = getattr(event, "content", None)
        for part in getattr(content, "parts", ()) or ():
            value = getattr(part, "text", None)
            if isinstance(value, str) and value.strip():
                text = value
    return text


def _json_safe(value: Any) -> Any:
    try:
        return json.loads(json.dumps(value, ensure_ascii=False))
    except (TypeError, ValueError) as exc:
        raise TypeError("Agent execution input must contain JSON-compatible values.") from exc

