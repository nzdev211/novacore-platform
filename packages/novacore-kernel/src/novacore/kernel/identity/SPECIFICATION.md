# Identity

The **Identity** bounded context defines the identity language of the Novacore Kernel.

It provides immutable, strongly-typed identity value objects that uniquely identify domain entities while remaining completely independent from infrastructure, runtime, persistence, and transport technologies.

Identity is the **foundation of the Kernel**. Every other bounded context depends on it.

---

# Purpose

The Identity module exists to model **identity as a domain concept**.

Its purpose is to provide a common, consistent, and type-safe identity model that every other bounded context can rely upon.

Identity is intentionally simple.

It owns one thing only:

> **Identity.**

---

# Responsibilities

The Identity bounded context is responsible for:

- Defining the identity language of the Kernel.
- Providing immutable identity value objects.
- Preventing identity confusion across domain types.
- Defining identity equality semantics.
- Providing stable string representations.
- Serving as the root dependency layer of the Kernel.

Identity is **not** responsible for:

- Identifier generation.
- Persistence.
- Authentication.
- Authorization.
- Infrastructure integration.
- Serialization frameworks.
- Runtime execution.

Identity owns **identity only**.

---

# Public Types

| Type | Description |
|------|-------------|
| `Identifier` | Base identity value object for the Kernel. |
| `ConversationId` | Identity of a Conversation. |
| `ExecutionId` | Identity of an Execution. |
| `WorkId` | Identity of a Work item. |
| `WorkerId` | Identity of a Worker. |
| `RequestId` | Identity of an incoming request. |
| `TraceId` | Identity of a distributed execution trace. |

---

# Design Principles

The Identity module follows several core principles.

## Immutable

Identifiers never change after construction.

Once created, an Identifier remains constant throughout its lifetime.

---

## Strongly Typed

Different domain concepts have different identifier types.

For example:

- `ConversationId`
- `WorkId`
- `ExecutionId`

Even when two identifiers share the same underlying value, they are **not considered equal** unless they are the same concrete type.

---

## Infrastructure Independent

Identity does not know about:

- UUID
- Firestore
- PostgreSQL
- FastAPI
- Google ADK
- Runtime
- Serialization frameworks

Identity models **what an identity is**, not **how it is generated or stored**.

---

## Value Object

Every identifier is modeled as a Value Object.

Identity is defined entirely by its value and concrete type.

Identifiers have no independent lifecycle.

---

# Dependency Layer

**Layer:** L0

Identity is the root of the Novacore dependency graph.

It has no dependencies on any other bounded context.

Allowed dependency:

- Python Standard Library

Forbidden dependencies include:

- Runtime
- Conversation
- Work
- Worker
- Execution
- Capability
- FastAPI
- Google ADK
- Firestore
- PostgreSQL
- Pydantic

---

# Usage

Applications should import identifiers through the package root.

```python
from novacore.kernel.identity import (
    Identifier,
    ConversationId,
    ExecutionId,
    WorkId,
    WorkerId,
    RequestId,
    TraceId,
)
```

Applications should never import internal implementation modules directly.

---

# Examples

Create identifiers.

```python
conversation_id = ConversationId(...)
execution_id = ExecutionId(...)
work_id = WorkId(...)
```

Equality.

```python
conversation_id == another_conversation_id
```

Result

```text
True
```

Cross-type equality.

```python
conversation_id == work_id
```

Result

```text
False
```

Dictionary usage.

```python
cache = {
    conversation_id: conversation
}
```

Because identifiers are immutable and hashable, they are safe dictionary keys.

---

# Architectural Rules

The Identity module follows these architectural rules.

- Identity owns identity only.
- Identity never owns generation strategies.
- Identity never owns persistence.
- Identity never owns infrastructure.
- Identity never depends on higher dependency layers.
- Invalid identifiers must never be constructible.
- Equality is based on both concrete type and value.

---

# Related Documents

| Document | Purpose |
|----------|---------|
| `SPECIFICATION.md` | Defines the complete domain contract and invariants. |
| `TEST_PLAN.md` | Defines how the Identity contract is verified through testing. |

---

# Future Evolution

Future versions may introduce:

- Identity generators
- UUIDv7 support
- ULID support
- KSUID support
- Snowflake support
- Pluggable generation strategies

These capabilities intentionally belong outside the Identity bounded context to preserve the architectural independence of the Kernel.

---

# Summary

The Identity bounded context is the foundation of the Novacore Kernel.

It establishes a common language for identity, provides immutable and strongly-typed value objects, and serves as the root dependency layer upon which every other bounded context is built.

Keeping Identity small, stable, and infrastructure-independent ensures that the Kernel remains portable, maintainable, and capable of evolving independently from runtime implementations.