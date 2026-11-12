# novacore-postgres

PostgreSQL persistence adapter package for Novacore.

**Status: scaffold only.** No repository implementations, SQL migrations, or database operations are included yet.

## Boundary

- Implements persistence ports defined by the application/Runtime boundary when finalized.
- Keeps PostgreSQL drivers, SQL, transactions, and row mapping inside this package.
- Does not define domain entities or domain invariants.
- Must not be imported by Kernel.
- May use `asyncpg` for the current asynchronous runtime, with `psycopg` available as an optional alternative if a concrete use case requires it.

## Installation

Choose a driver extra:

```bash
pip install 'novacore-postgres[asyncpg]'
# or
pip install 'novacore-postgres[psycopg]'
```

Connection strings and credentials must be provided through environment/secret management. Never commit credentials.

