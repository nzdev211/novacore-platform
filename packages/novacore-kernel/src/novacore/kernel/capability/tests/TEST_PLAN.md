# Tests for capability

# Capability Test Plan

**Module:** `novacore.kernel.capability`  
**Blueprint:** B002 — Capability Foundation  
**Version:** 0.1.0  
**Status:** Draft  
**Dependency Layer:** L1

---

# 1. Purpose

This document defines the verification strategy for the Capability bounded context.

Its purpose is to ensure every business rule, invariant, architectural constraint, and public contract defined in `SPECIFICATION.md` is verified through automated tests.

The objective of this test plan is **behavioral correctness**, not implementation coverage.

Every invariant MUST have at least one corresponding automated test.

---

# 2. Testing Principles

Capability follows the Novacore Kernel testing principles.

---

## Specification Driven

Tests validate the specification.

They never validate implementation details.

---

## Business Behavior Focused

Tests verify observable business behavior.

Internal implementation choices are irrelevant.

---

## Infrastructure Independent

Capability tests must never require:

- Runtime
- Worker implementations
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

Every test must produce the same result on every execution.

Capability tests must never rely on randomness.

---

## Fast

Capability tests should execute within milliseconds.

The Capability bounded context should never require expensive setup.

---

# 3. Test Categories

| Category | Purpose |
|----------|---------|
| Construction | Verify valid Capability creation |
| Immutability | Verify Capability cannot change |
| Business Semantics | Verify business meaning remains stable |
| Identity | Verify Capability identity behavior |
| Equality | Verify equality semantics |
| Dependency Rules | Verify architecture boundaries |
| Public API | Verify exported API |
| Invalid Construction | Reject invalid capabilities |
| Examples | Verify documented examples |

---

# 4. Invariant Verification Matrix

## Invariant 1

### Capability Is Immutable

Requirement

Capability cannot be modified after construction.

Tests

- Create Capability
- Attempt mutation
- Verify mutation fails
- Verify original values remain unchanged

Expected Result

Mutation is impossible.

---

## Invariant 2

### Stable Identity

Requirement

Every Capability owns exactly one CapabilityId.

Tests

- Construct Capability
- Verify CapabilityId exists
- Verify CapabilityId never changes

Expected Result

CapabilityId remains constant.

---

## Invariant 3

### Stable Meaning

Requirement

The semantic meaning of a Capability never changes.

Tests

- Construct Capability
- Verify name remains unchanged
- Verify immutable business meaning

Expected Result

Capability meaning remains stable.

---

## Invariant 4

### Human Readable Name

Requirement

Every Capability has a human-readable name.

Tests

- Construct Capability with valid name
- Verify name exists
- Verify name is accessible

Expected Result

Capability exposes one business name.

---

## Invariant 5

### Technology Independence

Requirement

Capability definitions must remain technology independent.

Tests

Attempt to create Capabilities using names such as:

- GPT-4 Processor
- Gemini Worker
- FastAPI Endpoint
- Firestore Query

Expected Result

Construction is rejected according to business naming rules.

---

## Invariant 6

### Reusable

Requirement

One Capability may be reused by multiple Work items.

Tests

- Associate one Capability with multiple Work definitions

Expected Result

Capability remains reusable.

---

## Invariant 7

### Infrastructure Independence

Requirement

Capability remains valid regardless of runtime implementation.

Tests

Verify Capability has no references to:

- Runtime
- Worker
- Google ADK
- FastAPI
- Firestore

Expected Result

Capability remains infrastructure independent.

---

# 5. Business Semantics Tests

Capability answers exactly one business question.

> What can be done?

Tests verify that Capability never answers:

- Who performs it?
- How it is implemented?
- Which model executes it?
- Which framework executes it?

Expected Result

Capability models business ability only.

---

# 6. Construction Tests

Verify successful construction.

Examples

```python
Capability(
    id=CapabilityId(...),
    name="Generate Image",
)
```

Expected Result

Construction succeeds.

---

```python
Capability(
    id=CapabilityId(...),
    name="Translate Text",
)
```

Expected Result

Construction succeeds.

---

# 7. Invalid Construction Tests

The following Capability definitions are invalid.

| Input | Expected |
|--------|----------|
| Empty name | Exception |
| Whitespace-only name | Exception |
| Missing CapabilityId | Exception |
| Mutable Capability | Exception |
| Technology-specific name | Exception |
| Infrastructure-specific name | Exception |

Construction must fail immediately.

---

# 8. Equality Tests

Capabilities are compared by identity.

Tests

Same CapabilityId

Expected

Equal

---

Different CapabilityId

Expected

Not Equal

---

Different Capability names

Expected

Not Equal

---

# 9. Public API Tests

Verify only supported public types are exported.

Expected exports

```python
Capability
CapabilityId
```

Applications import using

```python
from novacore.kernel.capability import (
    Capability,
    CapabilityId,
)
```

Internal modules are not part of the public contract.

---

# 10. Dependency Architecture Tests

Capability belongs to Layer L1.

Verify:

Capability imports only:

- Identity
- Python Standard Library

Capability imports none of:

- Work
- Worker
- Conversation
- Execution
- Runtime
- Google ADK
- FastAPI
- Firestore
- PostgreSQL

Expected Result

Architecture rules are satisfied.

---

# 11. Relationship Tests

Capability participates in the Kernel language.

Verify

One Capability may satisfy:

- one Work
- many Work items

Verify

One Worker may implement:

- one Capability
- many Capabilities

Capability itself never owns Work or Worker.

Expected Result

Relationships remain loosely coupled.

---

# 12. Documentation Examples

Every example documented in README.md and SPECIFICATION.md must compile and execute successfully.

Examples become executable documentation.

---

# 13. Regression Tests

Whenever a Capability bug is discovered:

1. Write a failing automated test.
2. Fix the implementation.
3. Verify the test passes.
4. Keep the regression test permanently.

Regression tests are never removed.

---

# 14. Definition of Done

Capability is considered fully verified when:

- Every invariant has an automated test.
- Every invalid construction scenario is tested.
- Business semantics are verified.
- Public API imports are verified.
- Architecture dependency rules are verified.
- Documentation examples execute successfully.
- All automated tests pass.

Only then may Blueprint B002 proceed to API Freeze.

---

# 15. Traceability Matrix

| Specification Requirement | Test Category |
|---------------------------|---------------|
| Immutable | Immutability Tests |
| Stable Identity | Identity Tests |
| Stable Meaning | Business Semantics Tests |
| Human Readable | Construction Tests |
| Technology Independent | Invalid Construction Tests |
| Reusable | Relationship Tests |
| Infrastructure Independent | Architecture Tests |
| Public API | Public API Tests |
| Documentation Examples | Documentation Tests |

Every requirement defined in `SPECIFICATION.md` MUST have at least one corresponding automated test.

No business rule is considered complete until it is verified.

---

# 16. Engineering Principles

Capability testing follows these engineering principles.

1. Test the specification, not the implementation.
2. Every invariant must be testable.
3. Every bug becomes a permanent regression test.
4. Architecture rules are verified automatically.
5. Documentation examples are executable.
6. Business semantics are protected by tests.
7. Capability remains infrastructure independent.
8. Tests must remain deterministic.
9. Tests must execute quickly.
10. Confidence is more important than code coverage.