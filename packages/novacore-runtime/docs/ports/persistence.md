# Persistence Ports — Design

**Status: Proposed; not frozen.**

## Purpose

Define Runtime/application-owned persistence boundaries implemented independently by Firestore and PostgreSQL adapters.

## Candidate repository responsibilities

- Persist and retrieve approved domain records.
- Support atomic operations where a use case requires them.
- Preserve identity and value semantics during serialization/deserialization.
- Make concurrency and transaction behavior explicit.

## Design constraints

- Do not expose Firestore document snapshots, collection references, SQL rows, sessions, or driver connections.
- Do not define persistence interfaces inside Kernel.
- Do not assume Firestore and PostgreSQL have identical transaction or query semantics.
- Avoid a generic `Repository[T]` abstraction until repeated concrete requirements justify it.
- Keep mapping and schema/migration concerns inside each persistence adapter.

## Implementation gate

First identify which objects must survive process restarts and the consistency boundaries for creating/updating Activity, Work, Assignment, and Execution. Then define the smallest repository ports needed by those use cases.

