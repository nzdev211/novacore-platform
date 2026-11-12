# Novacore Platform — Dependency Layers

The dependency direction is inward. Outer packages may depend on inner contracts; inner packages must not import outer implementations.

```text
Inbound adapters       novacore-fastapi
                             |
                             v
Runtime                 novacore-runtime
                         /    |     \
                        v     v      v
                 OpenAI   Anthropic  Google ADK
                 adapter   adapter   adapter
                        \    |     /
                         v   v    v
                    Runtime-defined ports
                             |
                             v
Kernel                 novacore-kernel
                             |
                             v
Foundation             novacore-foundation (only shared primitives)

Persistence adapters: novacore-firestore, novacore-postgres
Observability/testing: supporting packages; no domain ownership
```

## Rules

1. `novacore-kernel` must not import FastAPI, OpenAI, Anthropic, Google ADK, Firestore, PostgreSQL, or provider SDKs.
2. `novacore-runtime` owns orchestration and provider-independent ports required by its use cases.
3. `novacore-openai`, `novacore-anthropic`, and `novacore-google-adk` implement Runtime-facing integrations; they do not define domain entities.
4. `novacore-fastapi` translates transport input/output and invokes Runtime entry points. It does not contain domain rules.
5. Persistence adapters implement persistence boundaries required by Runtime/application services; they do not own domain semantics.
6. Provider selection and model configuration belong in runtime composition/configuration, not in Kernel entities.
7. Avoid cross-provider imports. OpenAI and Anthropic adapters must not depend on each other.
8. Do not add an abstraction solely to make providers look identical. Normalize only the capabilities the Creative Studio actually needs.

## Dependency summary

| Package | May depend on | Must not depend on |
|---|---|---|
| Kernel | Foundation | Runtime, provider SDKs, web frameworks, databases |
| Runtime | Kernel, Foundation | Concrete provider/database implementations |
| FastAPI adapter | Runtime contracts | Provider SDKs for direct model calls |
| OpenAI adapter | Runtime ports/contracts, OpenAI SDK | Anthropic SDK, Kernel implementation details beyond public domain types |
| Anthropic adapter | Runtime ports/contracts, Anthropic SDK | OpenAI SDK, Kernel implementation details beyond public domain types |
| Google ADK adapter | Runtime ports/contracts, Google ADK | Provider-specific adapter implementations |
| Firestore/Postgres | Runtime persistence ports/contracts, respective SDK/driver | Other persistence adapters |

