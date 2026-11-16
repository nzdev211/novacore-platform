# Running the Phase 35 Live ADK + Firestore Emulator Test

## 1. Install optional dependencies

From the Novacore repository root:

```bash
python -m pip install -e packages/novacore-kernel
python -m pip install -e packages/novacore-runtime
python -m pip install -e 'packages/novacore-fastapi[fastapi]'
python -m pip install -e packages/novacore-firestore
python -m pip install -e 'packages/novacore-google-adk[google-adk]'
python -m pip install 'google-cloud-firestore>=2.0' pytest
```

## 2. Start Firestore Emulator

For example, with the Google Cloud CLI:

```bash
gcloud emulators firestore start --host-port=127.0.0.1:8089
```

Keep that process running in another terminal.

## 3. Configure the live test

```bash
export FIRESTORE_EMULATOR_HOST="127.0.0.1:8089"
export GOOGLE_CLOUD_PROJECT="novacore-phase35-emulator"
export GOOGLE_API_KEY="YOUR_GOOGLE_AI_STUDIO_API_KEY"
export NOVACORE_RUN_LIVE_ADK_TESTS="1"
export NOVACORE_ADK_MODEL="gemini-2.5-flash"
```

Use a valid model available to your Google API project. The model can be
changed with `NOVACORE_ADK_MODEL` without changing the test.

## 4. Run the live integration test

```bash
pytest -v tests/integration/test_revision_workflow_live_adk_firestore.py
```

The test makes a real model request and can incur API charges. Do not set the
opt-in flag in general CI or routine unit-test environments.

## 5. Run ordinary tests

Without `NOVACORE_RUN_LIVE_ADK_TESTS=1`, the live test is skipped:

```bash
pytest -q packages/novacore-runtime/tests
pytest -q packages/novacore-google-adk/tests
pytest -q packages/novacore-firestore/tests
```

## Expected outcome

The API returns HTTP 202, the new Execution lifecycle is SUCCEEDED, the
persisted output contains `PHASE35_LIVE_ADK_OK`, a new PENDING review points to
that Execution, and replaying the same idempotency key returns the same
Execution and Review IDs with `replayed=true`.

