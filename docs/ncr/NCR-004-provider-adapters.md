# NCR-004: Separate AI Provider Adapter Packages

- Status: Accepted
- Date: 2026-11-12

## Context

Novacore needs to integrate OpenAI GPT models and Anthropic Claude models while preserving a vendor-independent Kernel and Runtime.

## Decision

Create independent distributions `novacore-openai` and `novacore-anthropic`. Keep `novacore-google-adk` as a separate Google agent-framework integration. Runtime defines provider-independent ports only where required by concrete use cases; each adapter implements those ports.

Do not create `novacore-chatgpt-claude` or a mandatory umbrella `novacore-adapters` package. `Adapters` describes an architectural role, not a required package boundary.

## Consequences

- Providers can be installed, tested, versioned, and replaced independently.
- Kernel remains free of vendor dependencies.
- Runtime owns orchestration and stable ports.
- Provider-specific capabilities must not be flattened prematurely into a lowest-common-denominator interface.
- Provider SDK dependencies are added when executable integration code is introduced.

