# Capability Specification

**Module:** `novacore.kernel.capability`  
**Blueprint:** B002 — Capability Foundation  
**Version:** 0.1.0  
**Status:** Draft  
**Dependency Layer:** L1

---

# 1. Purpose

The Capability bounded context defines the business language of abilities within the Novacore Kernel.

A Capability represents **what can be done**, independent of **who performs it**, **how it is implemented**, or **where execution occurs**.

Capability allows business intent to remain independent from runtime implementation.

It forms the contract between **Work** (requirements) and **Worker** (implementations).

---

# 2. Scope

## Included

The Capability bounded context includes:

- Capability
- CapabilityId

---

## Explicitly Excluded

The Capability bounded context MUST NOT contain:

- Worker implementations
- Runtime execution
- Execution planning
- Agent definitions
- Tool implementations
- Prompt templates
- AI model providers
- Google ADK
- FastAPI
- Firestore
- PostgreSQL
- HTTP
- Authentication
- Authorization
- Infrastructure adapters

These concerns belong to higher dependency layers.

---

# 3. Definition

A Capability is an immutable business definition describing an ability that may be required by Work and provided by one or more Workers.

Capability represents business meaning only.

Capability never represents implementation.

Examples include:

- Translate Text
- Generate Image
- Review Proposal
- Summarize Document
- Generate SQL
- Extract Structured Data

These describe business abilities, not technical implementations.

---

# 4. Responsibilities

The Capability bounded context is responsible for:

- Defining business abilities.
- Providing immutable capability definitions.
- Providing unique capability identities.
- Establishing a common business vocabulary.
- Allowing Work to express required abilities.
- Remaining independent from execution.

Capability is NOT responsible for:

- Executing work.
- Selecting Workers.
- Planning execution.
- Routing requests.
- AI model selection.
- Prompt engineering.
- Infrastructure integration.

Capability owns business ability only.

---

# 5. Domain Model

```
Capability

├── CapabilityId
└── Name
```

Capability is a business concept.

CapabilityId uniquely identifies the capability.

The Name describes the business ability in a human-readable form.

---

# 6. Public Types

## Capability

Represents one business capability.

A Capability is immutable after construction.

---

## CapabilityId

Represents the immutable identity of one Capability.

CapabilityId follows the Identity bounded context specification.

---

# 7. Business Semantics

Capability answers one business question:

> **What can be done?**

Capability never answers:

- Who performs it?
- How is it implemented?
- Which AI model is used?
- Which framework executes it?
- Which infrastructure performs it?

Those responsibilities belong to Worker and Runtime.

---

# 8. Invariants

The following conditions MUST always hold true.

---

## 8.1 Immutable

Capabilities are immutable.

Once created, a Capability never changes.

---

## 8.2 Stable Identity

Every Capability has exactly one CapabilityId.

The identity never changes.

---

## 8.3 Stable Meaning

The semantic meaning of a Capability remains constant.

Changing the meaning of a Capability requires defining a new Capability.

---

## 8.4 Human Readable

Every Capability has a human-readable name.

The name communicates business intent.

---

## 8.5 Technology Independent

Capability definitions must never reference:

- Gemini
- GPT
- Claude
- Python
- Google ADK
- HTTP
- Firestore
- FastAPI

Capabilities describe business language only.

---

## 8.6 Reusable

A Capability may be required by multiple Work items.

A Capability may be implemented by multiple Workers.

---

## 8.7 Infrastructure Independent

Capability definitions remain valid regardless of:

- runtime
- deployment environment
- execution framework
- cloud provider
- AI provider

---

# 9. State Machine

Capabilities are immutable domain definitions.

They do not have an operational lifecycle.

```
Created

↓

Stable
```

No additional state transitions exist.

---

# 10. Relationships

Capability participates in the Kernel language through the following relationships.

```
Work

requires

↓

Capability

implemented by

↓

Worker
```

Capability never owns Work.

Capability never owns Worker.

It exists independently.

---

# 11. Dependency Rules

Dependency Layer:

**L1**

---

## Allowed Dependencies

- Identity
- Python Standard Library

---

## Forbidden Dependencies

Capability MUST NOT depend on:

- Work
- Worker
- Conversation
- Execution
- Events
- Runtime
- Google ADK
- FastAPI
- Firestore
- PostgreSQL
- Infrastructure

Dependencies always point downward.

---

# 12. Public Import Contract

Applications SHOULD import Capability through the package root.

```python
from novacore.kernel.capability import (
    Capability,
    CapabilityId,
)
```

Applications SHOULD NOT import internal implementation modules.

The package root defines the supported public API.

---

# 13. Examples

Example Capability

```
Capability

Name

Generate Image
```

---

Another Capability

```
Capability

Name

Translate Text
```

---

Another Capability

```
Capability

Name

Generate SQL
```

Notice that no example references:

- Gemini
- OpenAI
- Claude
- Google ADK

Capability remains technology independent.

---

# 14. Invalid States

Invalid Capability definitions must never be constructible.

The following are invalid:

- Empty name
- Whitespace-only name
- Missing CapabilityId
- Mutable Capability
- Technology-specific capability names
- Infrastructure-specific capability names

Construction MUST fail immediately when invalid states are detected.

---

# 15. Non Goals

Capability intentionally does not model:

- Workers
- Agents
- Tools
- APIs
- Runtime execution
- Scheduling
- Routing
- Prompt templates
- AI providers
- Infrastructure

Those belong to higher dependency layers.

---

# 16. Design Rationale

Capability separates **business language** from **execution technology**.

Business logic should express required abilities.

Execution systems should decide how those abilities are fulfilled.

This separation allows:

- multiple Worker implementations
- multiple AI providers
- multiple execution runtimes
- future infrastructure evolution

without changing the Kernel language.

---

# 17. Future Evolution

Future versions may introduce:

- CapabilityVersion
- CapabilityCategory
- CapabilityTags
- CapabilityMetadata
- CapabilityAliases
- CapabilityComposition
- CapabilityDependencies

These concepts are intentionally excluded from Blueprint B002.

---

# 18. Architectural Principles

The Capability bounded context follows these principles.

1. Capability models business ability.
2. Capability is immutable.
3. Capability is technology independent.
4. Capability is reusable.
5. Capability does not execute work.
6. Capability does not select Workers.
7. Capability is infrastructure independent.
8. Work depends on Capability.
9. Worker implements Capability.
10. Runtime binds Work to Worker through Capability.

---

# 19. Exit Criteria

Blueprint B002 is complete when:

- Capability language is finalized.
- Business semantics are documented.
- Public API is frozen.
- Invariants are documented.
- Unit tests verify every invariant.
- Examples are complete.
- Dependency rules are enforced.
- No runtime or infrastructure dependencies exist.

Only after these conditions are satisfied may the project proceed to the next Blueprint.