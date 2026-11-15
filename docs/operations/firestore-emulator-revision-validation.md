# Running Firestore Emulator Revision Tests

## Prerequisites

- Python dependencies for the Novacore packages and test suite.
- `novacore-firestore[firestore]` installed (includes `google-cloud-firestore`).
- A running Firestore Emulator.

## Environment

Set the emulator host and a test project ID in the shell that runs pytest:

```bash
export FIRESTORE_EMULATOR_HOST="127.0.0.1:8080"
export GOOGLE_CLOUD_PROJECT="novacore-firestore-test"
```

The emulator host must point to the running emulator. The test suite does not start or manage the emulator process.

## Run revision persistence tests

From the repository root, with package `src` directories available on `PYTHONPATH`:

```bash
pytest -q \
  packages/novacore-firestore/tests/test_revision_store.py \
  packages/novacore-firestore/tests/test_revision_integration.py \
  packages/novacore-firestore/tests/integration/test_revision_firestore_emulator.py
```

The broader Firestore Emulator workflow test can also be run:

```bash
pytest -q packages/novacore-firestore/tests/integration
```

Without `FIRESTORE_EMULATOR_HOST`, Emulator tests are skipped. If `google-cloud-firestore` is not installed, the Emulator modules are skipped during collection. Fake-client/unit tests remain runnable without a live Emulator.

The revision Emulator tests use unique document IDs and remove the documents they create. For disposable test projects, it is still good practice to use a dedicated emulator instance rather than a shared development database.

