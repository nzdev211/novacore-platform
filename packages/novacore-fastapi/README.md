# novacore-fastapi

FastAPI inbound HTTP adapter for Novacore Platform.

**Status: scaffold only.** No HTTP routes or Runtime invocation handlers are implemented yet.

## Boundary

- Translates HTTP requests and responses at the platform boundary.
- Invokes application/Runtime entry points through stable public contracts.
- Keeps FastAPI, Pydantic transport schemas, HTTP status codes, and serialization concerns outside Kernel.
- Does not contain domain rules, assignment policy, or provider-specific model calls.
- Must not make Kernel or Runtime depend on FastAPI.

## Installation

Install the optional web dependencies:

```bash
pip install 'novacore-fastapi[fastapi]'
```

The application composition root should wire Runtime services and adapters into the API. Configuration and credentials must come from environment/secret management, never source control.

