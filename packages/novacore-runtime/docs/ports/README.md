# Runtime Ports

This directory records the contract boundaries for external integrations. It is a design specification, not yet an executable API.

## Port groups

1. Model generation: OpenAI and Anthropic API integrations.
2. Agent execution: Google ADK integration.
3. Persistence: Firestore and PostgreSQL implementations.
4. Inbound application entry points: FastAPI invokes Runtime use cases; it is not a Runtime dependency.

## Contract design rules

- Model generation and agent execution are separate capabilities. Do not force Google ADK into a chat-completion-shaped interface.
- Keep provider-specific request/response types inside provider adapters.
- Define only the common semantics actually required by Creative Studio.
- Persistence contracts should be defined around approved domain operations and consistency needs, not around database CRUD convenience.
- No SDK imports, network calls, credentials, or database drivers in this package.

