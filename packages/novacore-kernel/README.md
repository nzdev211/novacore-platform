# Novacore Kernel v0.1

A minimal, immutable domain model package for Novacore. The Kernel defines domain concepts and invariants; runtime orchestration, persistence, ID generation, and external adapters remain outside this package.

## Active bounded contexts

- `identity` — strongly typed immutable identifiers
- `request` — incoming request description
- `context` — context identity and immutable context attributes
- `objective` — desired outcome description
- `activity` — business effort and lifecycle status
- `planning` — activity-level planning record
- `capability` — capability definition
- `work` — unit of work
- `contract` — work-level contract description
- `worker` — execution resource and its capability references
- `assignment` — allocation of work to a worker
- `execution` — an execution attempt associated with an assignment

## Domain rules

- All domain entities and value objects are immutable.
- IDs are supplied by callers; the Kernel does not generate identifiers.
- Entity equality and hashing are based on concrete entity type and ID.
- Value-object equality and hashing are based on value.
- Cross-object relationship checks belong to an application/domain service, not entity constructors.
- Runtime adapters and infrastructure dependencies are excluded.

## Installation and tests

Install the package in editable mode with its test extra:

```bash
python -m pip install -e ".[test]"
pytest
```

Or run tests without installing:

```bash
PYTHONPATH=src pytest -q
```

## Deferred by design

Execution status, result, timestamps, retry policy, persistence, aggregate hydration, orchestration, and ID generation are not part of this v0.1 model. The prior `conversation` design is superseded by `context` in the active model. Historical planning/specification files are retained for traceability and should not be treated as implemented API.

