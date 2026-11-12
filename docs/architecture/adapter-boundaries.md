# Adapter Boundaries

## Provider integrations

Novacore treats OpenAI, Anthropic, and Google ADK as separate integrations because they expose different APIs, execution semantics, tool-use models, and operational concerns.

- `novacore-openai` integrates OpenAI APIs and GPT-family models.
- `novacore-anthropic` integrates Anthropic APIs and Claude-family models.
- `novacore-google-adk` integrates the Google Agent Development Kit and its agent execution model.

ChatGPT and Claude refer here to models accessed through their respective developer APIs. These packages do not automate the consumer ChatGPT or Claude websites.

## Runtime-owned ports

The Runtime should define only the provider-independent request/response or execution contracts that actual use cases require. Provider packages implement those ports. Do not place provider SDK types in Runtime public contracts.

The exact port shape is intentionally deferred until the Creative Studio runtime use cases are finalized. In particular, do not assume all providers share identical streaming, tool calling, multimodal, structured-output, or agent semantics.

## Composition

The application composition root selects and configures concrete adapters. API keys and provider settings come from environment/secret management, never from Kernel objects or source control.

## Current scaffold status

`novacore-openai` and `novacore-anthropic` are package scaffolds only. They do not yet send API requests. SDK dependencies and provider-specific implementations should be added with the first executable adapter slice and its contract tests.

