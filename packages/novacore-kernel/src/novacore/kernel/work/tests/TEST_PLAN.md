# Tests for work

# Work Test Plan

**Module:** `novacore.kernel.work`

**Blueprint:** B003 — Work Foundation

**Version:** 0.1.0

**Status:** Draft

**Dependency Layer:** L4

---

# 1. Purpose

This document defines the verification strategy for the Work bounded context.

Its purpose is to ensure every business rule, invariant, architectural constraint, and public contract defined in `SPECIFICATION.md` is verified through automated tests.

The objective of this test plan is **behavioral correctness**, not implementation coverage.

Every invariant MUST have at least one corresponding automated test.

---

# 2. Testing Principles

The Work bounded context follows the Novacore Kernel testing principles.

---

## Specification Driven

Tests verify the public specification.

Implementation details are not part of the contract.

---

## Business Behavior Focused

Tests validate business semantics.

Tests do not validate implementation techniques.

---

## Aggregate Integrity

Tests ensure the Work aggregate remains internally consistent.

Invalid Work objects must never exist.

---

## Infrastructure Independent

Tests must never require:

- Runtime
- Worker implementations
- Execution engine
- FastAPI
- Google ADK
- Firestore
- PostgreSQL
- HTTP
- Network
- File System

All tests execute entirely in memory.

---

## Deterministic

Every test must produce identical results.

Randomness is forbidden unless explicitly controlled.

---

## Fast

Work tests should execute within milliseconds.

No expensive runtime setup is permitted.

---

# 3. Test Categories

| Category | Purpose |
|----------|---------|
| Construction | Verify valid Work creation |
| Aggregate Integrity | Verify Work consistency |
| Immutability | Verify Work cannot change |
| Identity | Verify WorkId behavior |
| Value Semantics | Verify equality and hashing |
| Business Semantics | Verify executable objective behavior |
| Capability Rules | Verify required capability constraints |
| Invalid Construction | Reject invalid Work definitions |
| Architecture | Verify dependency boundaries |
| Public API | Verify exported API |
| Documentation | Verify examples compile |

---

# 4. Invariant Verification Matrix

## Invariant 1

### Work Is Immutable

Requirement

A Work cannot change after construction.

Tests

- Construct Work
- Attempt mutation
- Verify mutation fails
- Verify original values remain unchanged

Expected Result

Mutation is impossible.

---

## Invariant 2

### Stable Identity

Requirement

Every Work owns exactly one WorkId.

Tests

- Construct Work
- Verify WorkId exists
- Verify WorkId never changes

Expected Result

Stable identity.

---

## Invariant 3

### Represents One Objective

Requirement

A Work represents one executable business objective.

Tests

- Construct Work
- Verify only one business objective exists

Expected Result

Multiple unrelated objectives cannot exist inside one Work.

---

## Invariant 4

### Independently Executable

Requirement

Every Work represents one independently executable objective.

Tests

- Verify Work has complete business meaning
- Verify Work does not depend on runtime state

Expected Result

Work remains executable regardless of runtime implementation.

---

## Invariant 5

### Capability Driven

Requirement

Every Work requires one or more Capabilities.

Tests

- Construct Work with one Capability
- Construct Work with multiple Capabilities
- Construct Work without Capabilities

Expected Result

Construction without Capabilities fails.

---

## Invariant 6

### Desired Outcome

Requirement

Every Work defines one desired business outcome.

Tests

- Construct Work with valid DesiredOutcome
- Construct Work without DesiredOutcome

Expected Result

Missing DesiredOutcome is rejected.

---

## Invariant 7

### Technology Independent

Requirement

Work definitions remain technology independent.

Tests

Attempt to create Work such as:

- Execute GPT Prompt
- Call Gemini API
- Run FastAPI Endpoint

Expected Result

Rejected.

---

## Invariant 8

### Infrastructure Independent

Requirement

Work contains no infrastructure concerns.

Tests

Verify Work has no references to:

- Runtime
- HTTP
- Firestore
- Google ADK
- Database

Expected Result

Architecture remains clean.

---

# 5. Aggregate Tests

Verify Work behaves as one complete aggregate.

Tests

- Aggregate always valid after construction.
- Aggregate cannot exist partially initialized.
- Aggregate protects all invariants.
- Aggregate exposes only public API.

Expected Result

Aggregate remains internally consistent.

---

# 6. Construction Tests

Valid construction examples.

```python
Work(
    id=WorkId(...),
    name="Generate Product Logo",
    capabilities=[GenerateImage],
    priority=High,
    desired_outcome=DesiredOutcome(...),
)
```

Expected Result

Construction succeeds.

---

```python
Work(
    id=WorkId(...),
    name="Translate Documentation",
    capabilities=[TranslateText],
    priority=Normal,
    desired_outcome=DesiredOutcome(...),
)
```

Expected Result

Construction succeeds.

---

# 7. Invalid Construction Tests

The following definitions are invalid.

| Input | Expected |
|--------|----------|
| Missing WorkId | Exception |
| Empty name | Exception |
| Whitespace-only name | Exception |
| Missing DesiredOutcome | Exception |
| Empty Capability collection | Exception |
| Mutable Work | Exception |
| Multiple unrelated objectives | Exception |
| Technology-specific Work | Exception |

Construction must fail immediately.

---

# 8. Value Semantics Tests

Verify equality behavior.

Same WorkId

Expected

Equal

---

Different WorkId

Expected

Not Equal

---

Different object type

Expected

Not Equal

---

Hash consistency

Expected

Equal Work objects produce equal hashes.

---

# 9. Serialization Tests

Requirement

Work exposes stable domain values.

Tests

- Serialize Work
- Deserialize Work
- Verify identity preserved

Expected Result

Business meaning remains unchanged.

Serialization format is not tested.

---

# 10. Public API Tests

Verify supported public exports.

Expected exports

```python
Work
WorkId
WorkPriority
DesiredOutcome
```

Applications import using

```python
from novacore.kernel.work import (
    Work,
    WorkId,
    WorkPriority,
    DesiredOutcome,
)
```

Internal modules are not part of the public contract.

---

# 11. Architecture Tests

Verify Layer L4 dependency rules.

Allowed

- Identity
- Capability
- Context
- Objective
- Planning

Forbidden

- Worker
- Contract
- Execution
- Runtime
- Infrastructure
- Google ADK
- FastAPI
- Firestore

Expected Result

Dependency rules are satisfied.

---

# 12. Relationship Tests

Verify Work relationships.

Planning produces Work.

Work requires Capabilities.

Worker executes Work.

Execution references Work.

Events describe Execution.

Expected Result

Relationships remain loosely coupled.

---

# 13. Documentation Tests

Every example contained in:

- README.md
- SPECIFICATION.md

must compile and execute successfully.

Documentation becomes executable specification.

---

# 14. Regression Tests

Whenever a Work bug is discovered:

1. Write a failing automated test.
2. Fix the implementation.
3. Verify the test passes.
4. Keep the regression test permanently.

Regression tests are never removed.

---

# 15. Definition of Done

The Work bounded context is considered fully verified when:

- Every invariant has an automated test.
- Aggregate integrity is verified.
- Invalid construction is tested.
- Equality rules are verified.
- Hash behavior is verified.
- Public API is verified.
- Dependency rules are verified.
- Documentation examples compile.
- All automated tests pass.

Only then may Blueprint B003 proceed to API Freeze.

---

# 16. Traceability Matrix

| Specification Requirement | Test Category |
|---------------------------|---------------|
| Immutable | Immutability Tests |
| Stable Identity | Identity Tests |
| One Objective | Aggregate Tests |
| Capability Driven | Capability Tests |
| Desired Outcome | Construction Tests |
| Independently Executable | Business Semantics Tests |
| Technology Independent | Invalid Construction Tests |
| Infrastructure Independent | Architecture Tests |
| Public API Stability | Public API Tests |
| Dependency Rules | Architecture Tests |

Every requirement defined in `SPECIFICATION.md` MUST have at least one corresponding automated test.

No business rule is considered complete until it is verified.

---

# 17. Engineering Principles

The Work bounded context follows these engineering principles.

1. Test the specification, not the implementation.
2. Protect aggregate integrity.
3. Every invariant must be testable.
4. Invalid states must be impossible to construct.
5. Every bug becomes a permanent regression test.
6. Documentation examples are executable.
7. Architecture rules are automatically verified.
8. Tests remain deterministic.
9. Tests remain fast.
10. Confidence is more valuable than code coverage.