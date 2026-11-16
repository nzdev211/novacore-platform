# Phase 37 — Production Readiness Checklist

Use this as a release gate. Record an owner, evidence link, and completion date
for each applicable item in the host team's release process. A checked item
should have verifiable evidence, not just an assumption.

## A. Identity, authentication, and authorization

- [ ] API authentication is enabled for every non-public route.
- [ ] Resource-level authorization is checked for review, activity, work,
      execution, revision, and asset access.
- [ ] Tenant isolation is tested, including attempts to access another
      tenant's identifiers.
- [ ] Reviewer/creator/tenant identity is derived from the authenticated
      principal, never trusted from request JSON.
- [ ] ADK session identity is scoped to the intended tenant/user/worker and
      cannot collide across unrelated principals.
- [ ] Short-lived asset URLs are issued only after authorization.

## B. Secrets and Firestore access

- [ ] Production secrets are stored in a secret manager.
- [ ] No API keys or service-account credentials are committed to source control.
- [ ] Runtime service identities use least-privilege IAM.
- [ ] Development, staging, and production use separate cloud projects or
      equivalent isolated environments.
- [ ] Firestore access paths and required permissions are documented.
- [ ] Transport security and encryption-at-rest settings are verified.
- [ ] Server-side authorization is enforced independently of Firestore client
      security rules.

## C. Session and record retention

- [ ] Retention periods are approved for ADK sessions/events, workflow records,
      execution records, review/revision history, and external assets.
- [ ] ADK FirestoreSessionService collection/document layout is inspected for
      the exact pinned ADK version.
- [ ] No TTL policy is enabled on ADK collections until expiration semantics
      and related-document behavior are tested.
- [ ] Cleanup is tested in a non-production environment.
- [ ] Audit/review evidence remains available for the required retention period.

## D. Execution and recovery

- [ ] Phase 20–21 lifecycle transitions are tested against the production
      Firestore configuration in staging.
- [ ] An interrupted RUNNING execution is treated as uncertain and reconciled
      before any retry.
- [ ] SUCCEEDED executions return their persisted result rather than invoking
      the provider again.
- [ ] Idempotency behavior is tested for duplicate and concurrent requests.
- [ ] Provider idempotency guarantees, if relied upon, are documented.
- [ ] Operators have a documented procedure for unresolved RUNNING and FAILED
      executions.
- [ ] ADK session existence is never used as proof of Novacore execution success.

## E. Observability and incident response

- [ ] Structured logs include correlation IDs and relevant Novacore record IDs.
- [ ] Logs redact credentials, tokens, private prompts, and sensitive asset URLs.
- [ ] Metrics cover request latency, provider calls, Firestore failures,
      lifecycle transitions, review conflicts, and unresolved executions.
- [ ] Alerts and on-call ownership are defined.
- [ ] Incident procedures cover provider outage, Firestore outage, credential
      compromise, and stuck execution reconciliation.

## F. Capacity, deployment, and recovery

- [ ] Dependency versions are pinned and the deployment build is reproducible.
- [ ] Google ADK upgrades are tested in staging before production rollout.
- [ ] API timeouts, concurrency limits, and resource limits are configured.
- [ ] Automatic retries are limited to operations known to be safe.
- [ ] Firestore backup configuration is verified.
- [ ] A Firestore restore exercise has succeeded.
- [ ] External asset storage backup/restore has been tested.
- [ ] A rollback procedure is documented and tested.
- [ ] Production smoke tests do not use the Firestore Emulator or test credentials.

## G. Evidence from integration tests

- [ ] Phase 35 live ADK + Novacore Firestore revision integration test passed
      in the intended non-production cloud environment.
- [ ] Phase 36 ADK Firestore session recreation/recovery test passed against
      the intended non-production Firestore environment.
- [ ] The team records the exact ADK, Firestore client, Python, and model
      versions used for those runs.
- [ ] Test data cleanup is verified and does not remove production records.

## Release decision

- [ ] All critical items are complete or have an explicitly accepted risk owner.
- [ ] Operations/on-call owner has accepted the runbook.
- [ ] Security/privacy owner has reviewed data access and retention.
- [ ] Product owner has approved the release.

A local emulator pass alone does not satisfy production IAM, backup, retention,
availability, or security checks.

