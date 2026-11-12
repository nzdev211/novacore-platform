# novacore-firestore

Google Cloud Firestore persistence adapter package for Novacore.

**Status: scaffold only.** No repository implementations or database operations are included yet.

## Boundary

- Implements persistence ports defined by the application/Runtime boundary when finalized.
- Keeps Firestore SDK types, queries, transactions, and document mapping inside this package.
- Does not define domain entities or domain invariants.
- Must not be imported by Kernel.

## Installation

The Firestore SDK is an optional extra:

```bash
pip install 'novacore-firestore[firestore]'
```

Supply Google Cloud credentials through the deployment environment or secret manager. Never commit credentials.

