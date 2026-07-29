# Capability

The **Capability** bounded context defines the language of **business abilities** within the Novacore Kernel.

A Capability represents **what can be done**, independent of **who performs it**, **how it is performed**, or **where it is executed**.

Capabilities allow Work to describe required business abilities without coupling the domain model to specific Workers, AI models, tools, APIs, or infrastructure.

Capability is the second foundation of the Novacore Kernel and builds upon the Identity bounded context.

---

# Purpose

The Capability module exists to model **business abilities** as first-class domain concepts.

Instead of coupling business logic to concrete implementations, the Kernel expresses requirements using Capabilities.

For example:

- Translate Text
- Generate Image
- Summarize Document
- Extract Structured Data
- Review Proposal
- Generate SQL

These describe **what** the system is capable of doing.

They intentionally do not describe **how** the capability is implemented.

---

# Responsibilities

The Capability bounded context is responsible for:

- Defining business abilities.
- Providing immutable capability definitions.
- Providing unique identities for capabilities.
- Allowing Work to declare required abilities.
- Providing a stable business language shared across the Kernel.

Capability is **not** responsible for:

- Executing work.
- Selecting workers.
- Routing requests.
- Planning execution.
- Prompt engineering.
- AI model selection.
- Infrastructure integration.

Capability owns **business ability only**.

---

# Business Semantics

Capability answers one business question:

> **What can be done?**

Capability never answers:

- Who performs it?
- How is it implemented?
- Which AI model is used?
- Which API is called?
- Where does execution happen?

Those responsibilities belong to higher dependency layers.

---

# Public Types

| Type | Description |
|------|-------------|
| `Capability` | Represents one business capability. |
| `CapabilityId` | Immutable identity of a Capability. |

Future versions may introduce additional supporting types without changing the core concept.

---

# Examples

Examples of Capabilities include:

- Translate Text
- Summarize Document
- Generate Image
- Generate Marketing Copy
- Review Proposal
- Extract Structured Data
- Generate SQL
- Analyze Spreadsheet

These names represent business language.

They are intentionally independent of implementation technologies.

---

# Relationship to Other Bounded Contexts

Capability participates in the Kernel language through the following relationships.

```text
Work
    │
    │ requires
    ▼
Capability
    ▲
    │ implemented by
Worker
```

A Work declares the Capabilities it requires.

A Worker declares the Capabilities it provides.

The Runtime determines which Worker satisfies a required Capability.

This separation keeps business logic independent from execution technology.

---

# Dependency Layer

**Layer:** L1

Capability depends only on:

- Identity

Capability must never depend on:

- Work
- Worker
- Conversation
- Execution
- Runtime
- Events
- Infrastructure
- Frameworks

Dependency direction always flows toward lower layers.

---

# Architectural Rules

The Capability bounded context follows these architectural principles.

- Capability models business ability.
- Capability is technology independent.
- Capability is immutable.
- Capability does not execute work.
- Capability does not select Workers.
- Capability does not contain prompts.
- Capability does not reference AI providers.
- Capability exists independently of infrastructure.
- Capability is reusable across Work items.
- Capability forms part of the Kernel's ubiquitous language.

---

# Usage

Applications should import public types through the package root.

```python
from novacore.kernel.capability import (
    Capability,
    CapabilityId,
)
```

Applications should never import internal implementation modules directly.

---

# Examples

A Work requiring image generation.

```text
Work

Required Capability

Generate Image
```

A Worker implementing multiple capabilities.

```text
Worker

Provides

- Generate Image
- Remove Background
- Resize Image
```

Notice that neither Work nor Worker depends on implementation technology.

Both communicate using the Capability language.

---

# Related Documents

| Document | Purpose |
|----------|---------|
| `SPECIFICATION.md` | Defines the complete domain contract, business semantics, invariants, and dependency rules. |
| `TEST_PLAN.md` | Defines the verification strategy for Capability behavior and architectural constraints. |

---

# Future Evolution

Future versions may introduce:

- CapabilityVersion
- CapabilityCategory
- CapabilityTags
- CapabilityMetadata
- CapabilityAliases
- CapabilityRequirements
- CapabilityComposition

These enhancements must preserve the fundamental principle that Capability represents **what can be done**, never **how it is done**.

---

# Summary

Capability is the business language of ability within the Novacore Kernel.

It enables Work to express requirements independently of implementation, allows Workers to advertise the abilities they provide, and gives the Runtime a stable vocabulary for matching demand with execution.

By separating **business ability** from **execution technology**, the Capability bounded context helps keep the Kernel small, reusable, and independent of any specific runtime, AI provider, or infrastructure.