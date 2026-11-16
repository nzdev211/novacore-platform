# Phase 37 — Production Readiness and Operational Reliability

## Goal

Define the production-readiness boundary for the existing Novacore Creative
Studio workflow without changing the agreed architecture.

This phase converts known operational risks into explicit deployment and
release checks. It is a readiness specification, not a claim that the current
repository or a deployed environment already satisfies these checks.

## Architecture boundaries remain unchanged

- Kernel remains small and provider-independent.
- Runtime continues to own workflow orchestration, execution lifecycle,
  idempotency, recovery decisions, and human review.
- `novacore-google-adk` remains the Google ADK adapter.
- Google ADK's official `FirestoreSessionService` owns ADK conversation
  sessions and event history.
- Novacore Firestore stores continue to own workflow, execution, review, and
  revision records.
- FastAPI remains an inbound adapter; the host application owns authentication,
  authorization, tenant isolation, and deployment configuration.
- No new Kernel concepts, Runtime ports, or architectural layers are introduced.

## Production concerns

### 1. Identity and tenant isolation

Every API request must be authenticated. The host application must authorize
access to the specific review, activity, work, execution, and session being
requested. A valid user identity alone is not sufficient authorization.

Never accept `reviewer_id`, `creator_id`, tenant identity, or worker identity
as trusted authorization facts from an untrusted request body. Derive them from
the authenticated principal and server-side authorization context.

ADK session identity must be stable and scoped. The configured app name,
worker-specific user ID, and execution/session ID must not be shared across
unrelated tenants or users. Confirm this mapping in the host application before
production use.

### 2. Firestore access and data protection

Use separate service identities for environments where practical. Grant only
the Firestore permissions required by the deployed components and collections.
Do not use broad project-owner/editor credentials for application runtime.

Use TLS for network traffic and the cloud provider's encryption-at-rest
controls. Keep credentials in the deployment platform's secret manager; do not
commit API keys, service-account keys, or production environment files.

Firestore security rules are not a substitute for server-side IAM when the
backend accesses Firestore through privileged server credentials. Enforce
tenant and resource authorization in the host application and service layer.

### 3. Session retention and cleanup

Do not enable Firestore TTL on ADK session collections until the exact
`FirestoreSessionService` schema and expiration semantics for the pinned ADK
version have been inspected and tested. Deleting session documents prematurely
can break conversation continuity or leave related event data behind.

Define retention separately for:
- ADK session/event history;
- Novacore workflow and execution records;
- human review and revision history;
- externally stored media assets.

Retention must reflect product, contractual, and legal requirements. Test
cleanup against a non-production dataset and verify that deleting session
history does not delete workflow evidence needed for audit or review.

### 4. Execution safety and recovery

Preserve the existing Phase 20–21 lifecycle and recovery semantics:
- PENDING may be started according to the workflow's normal execution rules.
- RUNNING is an uncertain outcome after interruption; reconcile before retry.
- SUCCEEDED reuses the persisted result.
- FAILED requires the established recovery/review policy; do not silently
  create another provider invocation.

A persisted ADK conversation does not prove that a model invocation completed.
Do not infer execution success from the existence of an ADK session or events.
The Novacore ExecutionRecord remains the source of truth for execution status
and persisted output.

Provider idempotency can reduce duplicate effects only when the provider
supports and honors it. Novacore's idempotency reservation does not guarantee
exactly-once provider execution or exactly-once billing.

### 5. Observability

The host application should emit structured logs and metrics for:
- request correlation / trace ID;
- activity, work, assignment, execution, review, and revision identifiers;
- adapter operation and provider;
- execution lifecycle transitions;
- duration and outcome of model/agent calls;
- Firestore read/write/transaction failures;
- review and revision conflicts;
- recovery classifications and manual reconciliation actions.

Do not log API keys, access tokens, full prompts, private user content, or
sensitive asset URLs by default. Apply redaction and access controls to any
diagnostic data that could contain user content.

Alert on sustained provider failures, Firestore errors, elevated latency,
growing PENDING/RUNNING backlogs, and unresolved RUNNING executions. Thresholds
must be set from measured production behavior rather than guessed here.

### 6. Reliability and deployment

Use explicit dependency/version constraints and repeatable builds. Pin and
validate the Google ADK version used by the adapter. Test upgrades in a staging
environment before production rollout.

Configure bounded request timeouts and concurrency limits at the host/API
layer. Avoid adding automatic retries around non-idempotent agent calls. Retry
only operations whose semantics are known to be safe.

Before rollout, verify backup/restore procedures for Firestore and external
asset storage. A backup is not validated until a restore exercise has succeeded.

Use separate development, staging, and production projects/databases. Do not
run emulator integration tests against production resources.

## Release gate

Production deployment should be blocked until the host team has completed the
environment-specific checklist in
`docs/operations/phase-37-production-readiness-checklist.md`.

## Explicitly not delivered by this phase

- No production IAM policy or Firestore security rules.
- No TTL configuration or cleanup job.
- No deployment manifests, Terraform, or cloud infrastructure.
- No authentication provider integration or tenant authorization implementation.
- No metrics backend, dashboards, or alert rules.
- No automatic retry or recovery behavior changes.
- No live production Firestore validation.

These items require the target cloud project, host application, data policy,
and deployment environment. This patch records the required decisions and
verification steps without inventing those environment-specific details.

