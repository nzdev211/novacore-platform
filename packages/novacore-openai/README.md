# novacore-openai

OpenAI API adapter package for Novacore. Intended to connect Runtime-defined model/provider ports to OpenAI GPT models.

**Status: scaffold only.** No API requests or runtime adapter implementation are included yet.

## Boundary

- Implements provider-independent ports defined by `novacore-runtime` once those contracts are finalized.
- Keeps OpenAI SDK types and API details inside this package.
- Does not define Kernel entities or orchestration policy.
- Uses OpenAI developer APIs; it does not automate the ChatGPT consumer website.

## Installation

The `openai` SDK is an optional extra in this scaffold:

```bash
pip install 'novacore-openai[openai]'
```

API keys must be supplied through environment/secret management by the application composition root. Never commit credentials.

