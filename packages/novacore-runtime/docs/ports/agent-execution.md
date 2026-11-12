# Agent Execution Port — Design

**Status: Proposed; not frozen.**

## Purpose

Provide a Runtime-owned boundary for delegating an assigned unit of work to an agent framework, initially Google ADK.

## Responsibilities

- Translate an approved Assignment/Execution request into the agent framework's execution model.
- Pass the execution context and required inputs.
- Return execution progress/outcome in Runtime-owned terms.
- Keep ADK Runner, Session, RemoteA2aAgent, and SDK types inside `novacore-google-adk`.

## Separation from model generation

An agent framework manages agent execution, tools, sessions, and potentially multiple model interactions. It is not interchangeable with a direct model-generation API. OpenAI and Anthropic direct model adapters should not be forced to implement this port unless a later agent runtime actually requires it.

## Implementation gate

Define lifecycle, streaming/event delivery, cancellation, session/context mapping, and failure semantics from the first concrete agent workflow before freezing the protocol.

