# Phase 38 — Creative Studio Deployment Runbook

This is a provider-neutral runbook. Replace bracketed values with decisions
from the actual Creative Studio deployment. Do not paste secrets into this file.

## 1. Before deployment

- [ ] Identify the Creative Studio Next.js repository and commit to deploy.
- [ ] Identify the Novacore Platform commit/package versions used by the API.
- [ ] Identify the target hosting platform and deployment environment.
- [ ] Identify the Google Cloud project and Firestore database.
- [ ] Confirm Google ADK version and model selection.
- [ ] Confirm the authentication provider/gateway and trusted principal format.
- [ ] Confirm external asset storage and access policy.
- [ ] Confirm staging is isolated from production data and credentials.
- [ ] Confirm Phase 35 live revision test and Phase 36 ADK session recovery test
      have been run in a non-production environment; attach results.

## 2. Build and configuration

- [ ] Build the Python API from a clean environment using pinned dependencies.
- [ ] Build the Next.js application from a clean environment.
- [ ] Configure the server-side API origin and browser-facing API/proxy strategy.
- [ ] Configure CORS only for the intended origins if browser calls cross-origin.
- [ ] Configure authentication issuer/audience or trusted gateway settings.
- [ ] Configure Google Cloud workload identity or approved credential mechanism.
- [ ] Configure Firestore project/database and ADK session collection root.
- [ ] Configure external asset storage and protected URL resolution.
- [ ] Configure health/readiness checks and structured logging.
- [ ] Inject secrets through the platform secret manager.

Do not assume `NEXT_PUBLIC_NOVACORE_API_URL` is appropriate for every hosting
layout. It is browser-visible. Prefer a server-side proxy/BFF when the API
origin or credentials should not be exposed to the browser.

## 3. Deploy staging

1. Deploy API and workers/agents, if separately hosted.
2. Verify API health and readiness.
3. Verify the API is connected to the intended staging Firestore project.
4. Verify Google ADK credentials and a low-risk test invocation.
5. Deploy the Next.js application.
6. Verify browser-to-API routing and authentication.
7. Run the smoke-test plan.
8. Review logs and lifecycle records for the test activity.
9. Verify asset URLs are protected and expire as intended.
10. Record evidence in `phase-38-release-evidence-template.md`.

## 4. Production rollout

Proceed only after staging sign-off and Phase 37 release gate completion.

- [ ] Confirm production project, database, bucket and identity configuration.
- [ ] Confirm backup and restore evidence.
- [ ] Confirm IAM and tenant isolation review.
- [ ] Confirm rollback target and rollback owner.
- [ ] Deploy API using the approved rollout strategy.
- [ ] Run API health checks before exposing traffic.
- [ ] Deploy Next.js application.
- [ ] Run minimal production smoke tests with dedicated test identities/data.
- [ ] Confirm no test/emulator configuration is present.
- [ ] Monitor provider errors, Firestore failures, latency and unresolved RUNNING
      executions.

## 5. Rollback

Rollback criteria must be defined by the host team before deployment. Examples
include sustained authentication failures, tenant isolation defects, data
corruption, repeated Firestore transaction failures, or a provider failure rate
above the team's approved threshold.

Rollback steps:
1. Stop or reduce incoming traffic using the platform's deployment controls.
2. Revert API and/or frontend to the last known-good release.
3. Do not delete workflow, execution, review, revision, or ADK session records
   as part of application rollback.
4. Reconcile any executions left in RUNNING; do not blindly replay them.
5. Preserve logs and incident evidence.
6. Confirm service health and obtain release-owner approval before reopening
   traffic.

## 6. Post-deployment

- [ ] Verify dashboards and alerts.
- [ ] Verify on-call ownership and escalation.
- [ ] Verify backup jobs and retention policies.
- [ ] Review unresolved execution and revision reservations.
- [ ] Record deployed commit hashes and package versions.

