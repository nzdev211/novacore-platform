# novacore-google-adk

Google Agent Development Kit (ADK) integration package for Novacore.

**Status: scaffold only.** No agent execution adapter or API calls are implemented yet.

## Boundary

- Integrates Google ADK agent execution with Runtime-defined ports when those contracts are finalized.
- Keeps Google ADK types, sessions, runners, and A2A details inside this package.
- Does not define Kernel entities or own orchestration policy.
- Must not depend on `novacore-openai` or `novacore-anthropic`.

## Installation

The Google ADK dependency is an optional extra:

```bash
pip install 'novacore-google-adk[google-adk]'
```

Credentials and project configuration must be supplied through environment/secret management. Never commit credentials.

