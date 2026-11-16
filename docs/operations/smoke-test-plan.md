# Phase 38 — Creative Studio Smoke Test Plan

Run in staging first. Use dedicated test users, tenant data and assets. Do not
use production customer data for test execution.

## Test 1 — Authentication boundary

1. Open Creative Studio without an authenticated session.
2. Attempt to load a protected review.
3. Confirm the request is rejected or redirected according to the host policy.
4. Authenticate as a permitted reviewer and load the same review.

Expected: unauthenticated access is denied; permitted access succeeds.

## Test 2 — Resource and tenant isolation

1. Authenticate as a user from tenant A.
2. Request a known review belonging to tenant B.
3. Repeat for review context, history, revision and asset URLs.

Expected: access is denied without disclosing protected resource content.

## Test 3 — Review context and asset preview

1. Open a review with a seeded brief, shot specification and test assets.
2. Confirm the UI displays the brief and flexible shot specification.
3. Confirm supported image/video previews load through authorized URLs.
4. Confirm unavailable context does not prevent the review decision workflow
   from displaying its supported review state.

Expected: only authorized assets are available; the review context is associated
with the requested review and its execution.

## Test 4 — Human review

1. Submit a PENDING review decision using the approved reviewer account.
2. Confirm the decision is persisted.
3. Submit a second decision for the same review.

Expected: first decision succeeds; repeated/concurrent terminal decision is
rejected according to the existing conflict behavior.

## Test 5 — Revision and idempotency

1. Use a review in CHANGES_REQUESTED state.
2. Submit a revision with an idempotency key.
3. Confirm a new Execution and a new PENDING review are created.
4. Repeat the same request with the same idempotency key.
5. Confirm the same result is replayed and no second revision is created.

Expected: original records remain unchanged; the replay returns the same
execution/review identifiers.

## Test 6 — ADK session persistence

Run the Phase 36 test in the target non-production environment. Confirm that a
new executor/Runner can resume the same ADK session using the stable session
identity and retrieve earlier conversation context.

Expected: ADK session history persists. This does not establish that a
Novacore execution succeeded.

## Test 7 — Execution recovery

1. Inspect a PENDING execution.
2. Inspect a SUCCEEDED execution and confirm its stored result is reused.
3. In a controlled test, simulate interruption after RUNNING is persisted.
4. Confirm the recovery service classifies the outcome as uncertain.

Expected: no automatic duplicate provider invocation for uncertain RUNNING
execution.

## Test 8 — Operational telemetry

1. Run one successful review/revision flow.
2. Trigger a controlled authorization denial.
3. Trigger a controlled dependency failure in staging.
4. Inspect structured logs and metrics.

Expected: events can be correlated by trace and Novacore record IDs; secrets,
tokens and private prompt content are not exposed.

## Test 9 — Frontend/API deployment configuration

1. Verify the frontend calls the intended staging API.
2. Verify no secret is present in browser bundles or `NEXT_PUBLIC_*` settings.
3. Verify CORS or same-origin proxy behavior.
4. Verify the production build does not contain emulator endpoints.

Expected: requests route to the intended environment with no credential leakage.

## Evidence to retain

Record environment, commit hashes, package versions, test identity, timestamps,
result, and sanitized logs. Never include credentials, access tokens, or private
customer content in the evidence bundle.

