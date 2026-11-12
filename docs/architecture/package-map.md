# Novacore Platform — Package Map

## Architectural packages

| Package | Responsibility | Depends on |
|---|---|---|
| `novacore-kernel` | Domain identities, entities, value objects, invariants and domain contracts | `novacore-foundation` only where a genuine shared primitive is required |
| `novacore-runtime` | Planning, assignment, execution coordination and runtime ports | Kernel; Foundation where needed |

## Inbound and provider adapters

| Package | Responsibility | Direction |
|---|---|---|
| `novacore-fastapi` | HTTP transport, API endpoints and request/response mapping | Inbound adapter to Runtime |
| `novacore-google-adk` | Google ADK agent integration | Outbound/provider adapter |
| `novacore-openai` | OpenAI API integration for GPT models | Outbound/model-provider adapter |
| `novacore-anthropic` | Anthropic API integration for Claude models | Outbound/model-provider adapter |
| `novacore-google-adk` | Google ADK agent execution integration | Outbound/agent-framework adapter |

## Persistence and supporting packages

| Package | Responsibility |
|---|---|
| `novacore-firestore` | Firestore persistence adapter |
| `novacore-postgres` | PostgreSQL persistence adapter |
| `novacore-workers` | Worker-specific integrations and worker implementations; keep domain Worker in Kernel |
| `novacore-observability` | Logging, tracing and metrics integrations when introduced |
| `novacore-testing` | Shared test utilities and test fixtures when justified |

## Package naming rule

Use one package per independently versioned integration or infrastructure provider. `Adapters` is an architectural category, not a mandatory umbrella package. Do not create a redundant `novacore-adapters` package unless shared adapter infrastructure becomes substantial enough to justify it.

## Python import namespaces

- Distribution: `novacore-openai`; import namespace: `novacore.openai`
- Distribution: `novacore-anthropic`; import namespace: `novacore.anthropic`
- Distribution: `novacore-google-adk`; import namespace: `novacore.google_adk`
- Distribution: `novacore-firestore`; import namespace: `novacore.firestore`
- Distribution: `novacore-postgres`; import namespace: `novacore.postgres`

These are separate distributions and can be installed independently. The shared `novacore` namespace is intentionally a PEP 420 namespace package.

