# Phase 38 — Creative Studio Deployment Boundary

## Purpose

Turn Phase 37 production-readiness requirements into an explicit integration
boundary for the Creative Studio host application.

This document describes what belongs in each existing component. It does not
assume a specific hosting provider, identity provider, tenant model, or cloud
project.

## Existing architecture — unchanged

| Component | Responsibility at deployment |
|---|---|
| Next.js Creative Studio | User interface; calls the backend over HTTP |
| FastAPI host/API | HTTP boundary, request validation, dependency injection |
| Host application services | Authentication, resource authorization, tenant isolation, asset URL resolution |
| Novacore Runtime | Workflow orchestration, execution lifecycle, idempotency, recovery and review |
| Novacore Kernel | Provider-independent domain types and rules |
| Google ADK adapter | Agent execution and ADK session service integration |
| Firestore adapter | Workflow, execution, review and revision persistence |
| External asset storage | Image/video/file bytes; workflow records keep references |

Next.js does not import Python packages. It calls the FastAPI API over HTTP.

## Required host integration seams

The host application must provide and test these integration seams:

1. **Authenticated principal** — trusted user identity from the chosen identity
   provider or gateway.
2. **Resource authorization** — verifies that the principal may access the
   requested review/activity/work/execution and associated assets.
3. **Tenant resolution** — derives tenant scope from trusted authentication
   context and server-side records.
4. **Creator/reviewer dependencies** — inject authenticated identity into
   FastAPI route dependencies; never trust identity fields in request JSON.
5. **Review context resolver** — loads the exact review's brief, shot
   specification and authorized asset references.
6. **Revision source authorization** — verifies the exact source review,
   execution, activity and work before creating a revision.
7. **Asset URL resolver** — issues protected or short-lived URLs after
   authorization.
8. **Runtime/adapter construction** — wires the existing Runtime services to
   the configured Firestore and Google ADK adapters.

## Configuration contract

The exact variable names depend on the host repository. At minimum, deployment
configuration must identify:

- API base URL used by the Next.js server/browser as appropriate;
- environment name;
- Google Cloud project and Firestore database/namespace configuration;
- Google ADK model and approved provider authentication method;
- ADK session collection/root configuration;
- authentication issuer/audience or gateway trust configuration;
- external asset storage bucket/container;
- logging and telemetry exporter configuration.

Secrets must be injected by the deployment platform's secret manager. Never
expose provider credentials through `NEXT_PUBLIC_*` variables.

## Security boundary

- Browser-supplied IDs are selectors, not proof of authorization.
- The API must authenticate every protected request.
- The host must authorize every requested resource and enforce tenant isolation.
- Reviewer and creator identities come from authenticated server-side context.
- Asset URLs must not grant broader access than the authorized resource.
- Firestore server credentials must use least-privilege IAM.
- Logs must not expose credentials, tokens, private prompts, or sensitive URLs.

## Readiness boundary

The host application is deployable only after its own repository has concrete
implementations for the integration seams above and the Phase 37 release gate
has evidence. This patch does not claim those implementations already exist.

