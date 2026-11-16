# Phase 37 — Environment Configuration Template

This is a naming/reference template, not a ready-to-deploy environment file.
Populate values through the deployment platform's secret/configuration manager.
Do not commit populated secrets.

## Required configuration categories

| Category | Example variable | Handling |
|---|---|---|
| API | `NOVACORE_API_ENV` | Non-secret; set per environment |
| Google project | `GOOGLE_CLOUD_PROJECT` | Non-secret identifier |
| ADK model | `NOVACORE_ADK_MODEL` | Pin/approve per environment |
| Google API key (if API-key auth is used) | `GOOGLE_API_KEY` | Secret; secret manager only |
| Firestore credentials | Workload identity / ADC | Prefer workload identity; avoid key files |
| Firestore database | Host-specific database configuration | Non-secret identifier |
| Session collection root | Adapter configuration | Keep stable; isolate by environment |
| Logging level | Host logging configuration | Avoid verbose prompt/content logging |

## Operational rules

1. Prefer workload identity / Application Default Credentials in deployed
   Google Cloud environments.
2. Use a separate project/database and collection namespace for each
   environment.
3. Do not point local integration tests at production Firestore.
4. Do not place credentials in `NEXT_PUBLIC_*` variables or browser bundles.
5. Keep the same ADK session identity components when intentionally resuming a
   session; use a new execution/session identity for a new execution.
6. Do not add undocumented TTL fields or collection cleanup assumptions.
7. Keep API keys and access tokens out of logs and support bundles.

## Example local emulator variables

```bash
export FIRESTORE_EMULATOR_HOST="127.0.0.1:8089"
export GOOGLE_CLOUD_PROJECT="novacore-local"
export NOVACORE_ADK_MODEL="gemini-2.5-flash"
```

Add credentials only in your local shell or secret manager as appropriate.
The exact authentication mechanism depends on the selected Google integration
and deployment environment.

