# novacore-anthropic

Anthropic API adapter package for Novacore. Intended to connect Runtime-defined model/provider ports to Claude models.

**Status: scaffold only.** No API requests or runtime adapter implementation are included yet.

## Boundary

- Implements provider-independent ports defined by `novacore-runtime` once those contracts are finalized.
- Keeps Anthropic SDK types and API details inside this package.
- Does not define Kernel entities or orchestration policy.
- Uses Anthropic developer APIs; it does not automate the Claude consumer website.

## Installation

The `anthropic` SDK is an optional extra in this scaffold:

```bash
pip install 'novacore-anthropic[anthropic]'
```

API keys must be supplied through environment/secret management by the application composition root. Never commit credentials.

