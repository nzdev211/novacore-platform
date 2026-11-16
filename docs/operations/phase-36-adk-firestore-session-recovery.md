# Run the Phase 36 ADK Firestore session recovery test

The test is opt-in and makes two real Gemini API calls. It writes ADK session
records to a Firestore Emulator.

## Install

```bash
python -m pip install -e packages/novacore-kernel
python -m pip install -e packages/novacore-runtime
python -m pip install -e 'packages/novacore-google-adk[firestore]'
python -m pip install pytest
```

## Start Firestore Emulator

```bash
gcloud emulators firestore start --host-port=127.0.0.1:8089
```

In another terminal:

```bash
export FIRESTORE_EMULATOR_HOST="127.0.0.1:8089"
export GOOGLE_CLOUD_PROJECT="novacore-phase36-emulator"
export GOOGLE_API_KEY="YOUR_GOOGLE_AI_STUDIO_API_KEY"
export NOVACORE_RUN_LIVE_ADK_TESTS="1"
export NOVACORE_ADK_MODEL="gemini-2.5-flash"
```

Run from the repository root:

```bash
pytest tests/integration/test_google_adk_firestore_session_recovery.py -v
```

The test creates a unique ADK app name and Firestore root collection per run.
It does not delete the emulator collection automatically. Use the emulator's
administrative cleanup tooling when desired.

## Expected result

The first executor stores a phrase in an ADK conversation. A second executor is
constructed with a new Runner and Firestore session service. The second turn
must recall the phrase from the persisted conversation. Ordinary test runs skip
this test unless all opt-in environment variables are set.

A real Gemini API call may incur charges. Do not point this test at production
Firestore unless you intentionally want to create persistent session data.

