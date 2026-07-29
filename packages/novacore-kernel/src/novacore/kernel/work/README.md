# Work Specification

**Module:** `novacore.kernel.work`  
**Blueprint:** B003 — Work Foundation  
**Version:** 0.1.0  
**Status:** Draft  
**Dependency Layer:** L4

---

# 1. Purpose

The Work bounded context defines the language of **executable business objectives** within the Novacore Kernel.

A Work represents the smallest independently executable business objective produced through decomposition of an Objective by the Planning bounded context.

Work exists independently of runtime execution, infrastructure, AI models, and Workers.

It defines **what must be executed**, not **how execution occurs**.

---

# 2. Scope

## Included

The Work bounded context includes:

- Work
- WorkId
- WorkStatus
- WorkPriority
- WorkOutcome

---

## Explicitly Excluded

The Work bounded context MUST NOT contain:

- Planning algorithms
- Planner implementation
- Worker selection
- Runtime scheduling
- Runtime execution
- Retry policies
- Orchestration
- Prompt templates
- AI providers
- Google ADK
- FastAPI
- Firestore
- PostgreSQL
- Infrastructure adapters

These responsibilities belong to other bounded contexts or higher dependency layers.

---

# 3. Definition

A Work is the smallest independently executable business objective within the Novacore Kernel.

Work is produced by the Planning bounded context from an Objective.

A Work expresses:

- what must be accomplished
- which Capabilities are required
- the desired business outcome

A Work never expresses:

- who performs it
- how it executes
- where it executes
- which technology executes it

---

# 4. Responsibilities

The Work bounded context is responsible for:

- Representing executable business objectives.
- Providing immutable Work identities.
- Declaring required Capabilities.
- Defining desired business outcomes.
- Defining business priority.
- Defining business status.
- Remaining independent from runtime execution.

Work is NOT responsible for:

- Planning
- Worker selection
- Scheduling
- Execution
- Retry logic
- Infrastructure integration
- AI model selection
- Prompt engineering

Work owns executable business objectives only.

---

# 5. Domain Model

```
Work

├── WorkId
├── Name
├── RequiredCapabilities
├── WorkPriority
├── WorkStatus
└── WorkOutcome
```

Work is a business concept.

WorkId uniquely identifies the Work.

RequiredCapabilities define the business abilities necessary for successful execution.

WorkOutcome defines the desired business result.

---

# 6. Public Types

## Work

Represents one executable business objective.

---

## WorkId

Represents the immutable identity of a Work.

---

## WorkStatus

Represents the lifecycle state of a Work.

Examples may include:

- Planned
- Ready
- Running
- Completed
- Failed
- Cancelled

Status values may evolve in future versions.

---

## WorkPriority

Represents the business priority of a Work.

Priority influences planning decisions but never changes business meaning.

---

## WorkOutcome

Represents the desired business outcome produced by successful execution.

---

# 7. Business Semantics

Work answers one business question.

> **What must be executed?**

Work never answers:

- Why?
- Who?
- How?
- Where?

Those responsibilities belong to:

- Context
- Objective
- Planning
- Worker
- Runtime

---

# 8. Invariants

The following conditions MUST always hold true.

---

## 8.1 Immutable

Work is immutable.

Once created, a Work never changes.

---

## 8.2 Stable Identity

Every Work has exactly one WorkId.

The identity never changes.

---

## 8.3 Stable Meaning

The semantic meaning of a Work never changes.

Changing business intent requires creating a new Work.

---

## 8.4 Required Capabilities

Every Work declares one or more required Capabilities.

Capabilities describe business abilities only.

---

## 8.5 Technology Independent

Work definitions never reference:

- Gemini
- GPT
- Claude
- Google ADK
- Python
- FastAPI
- Firestore
- PostgreSQL

Work remains independent from implementation technologies.

---

## 8.6 Independently Executable

Every Work represents one independently executable business objective.

A Work should not require partial execution of another Work to define its own meaning.

Execution dependencies are modeled by the Planning bounded context.

---

## 8.7 Outcome Driven

Every Work exists to achieve one desired business outcome.

Execution success is measured against that outcome.

---

# 9. State Machine

A Work progresses through business lifecycle states.

```
Planned
    │
    ▼
Ready
    │
    ▼
Running
    │
 ┌──┴───────────┐
 ▼              ▼
Completed    Failed
                 │
                 ▼
            Cancelled
```

State transitions describe business lifecycle only.

Runtime implementation details remain outside this bounded context.

---

# 10. Relationships

```
Context

↓

Objective

↓

Planning

↓

Work

↓

Capability

↓

Worker

↓

Execution

↓

Event
```

Planning creates Work.

Work requires Capabilities.

Workers implement Capabilities.

Runtime executes Work.

Events record execution history.

---

# 11. Dependency Rules

Dependency Layer:

**L4**

---

## Allowed Dependencies

- Identity
- Capability
- Context
- Objective
- Planning
- Python Standard Library

---

## Forbidden Dependencies

Work MUST NOT depend on:

- Worker
- Contract
- Execution
- Event
- Runtime
- Infrastructure
- Google ADK
- FastAPI
- Firestore
- PostgreSQL

Dependencies always point downward.

---

# 12. Public Import Contract

Applications SHOULD import Work through the package root.

```python
from novacore.kernel.work import (
    Work,
    WorkId,
    WorkStatus,
    WorkPriority,
    WorkOutcome,
)
```

Applications SHOULD NOT import internal implementation modules.

The package root defines the supported public API.

---

# 13. Examples

Example

```
Work

Name

Translate Product Manual

Required Capability

Translate Text

Desired Outcome

Localized Product Manual
```

---

Example

```
Work

Name

Generate Marketing Banner

Required Capability

Generate Image

Desired Outcome

Approved Marketing Asset
```

---

Example

```
Work

Name

Summarize Sales Meeting

Required Capability

Summarize Document

Desired Outcome

Executive Summary
```

---

# 14. Invalid States

Invalid Work definitions must never be constructible.

The following are invalid:

- Missing WorkId
- Empty name
- Whitespace-only name
- Missing required Capability
- Mutable Work
- Missing desired outcome
- Technology-specific Work definitions

Construction MUST fail immediately.

---

# 15. Non Goals

The Work bounded context intentionally does not define:

- Planning strategies
- Execution logic
- Scheduling
- Worker assignment
- Retry policies
- Runtime state
- Prompt engineering
- AI providers
- Infrastructure integration

These concerns belong to Planning, Worker, Execution, or Runtime.

---

# 16. Design Rationale

Business intent should not be executed directly.

Objectives are often too large, ambiguous, or complex for direct execution.

The Planning bounded context decomposes Objectives into one or more independently executable Work items.

Each Work provides a stable, technology-independent representation of a business objective that can later be assigned to Workers and executed by the Runtime.

This separation allows planning strategies, execution technologies, and infrastructure to evolve independently while preserving the Kernel language.

---

# 17. Future Evolution

Future versions may introduce:

- WorkDependencies
- WorkGraph
- CompositeWork
- WorkConstraints
- WorkPolicies
- WorkTemplates
- WorkMetadata
- HumanApprovalRequirements

These concepts are intentionally excluded from Blueprint B003.

---

# 18. Architectural Principles

The Work bounded context follows these principles.

1. Work models executable business objectives.
2. Work is immutable.
3. Work is technology independent.
4. Work is outcome driven.
5. Work declares required Capabilities.
6. Work never performs execution.
7. Work never selects Workers.
8. Planning produces Work.
9. Runtime executes Work.
10. Work remains independent from infrastructure.

---

# 19. Exit Criteria

Blueprint B003 is complete when:

- Work language is finalized.
- Business semantics are documented.
- Public API is frozen.
- Invariants are documented.
- Unit tests verify every invariant.
- Dependency rules are enforced.
- Documentation examples are complete.
- No runtime or infrastructure dependencies exist.

Only after these conditions are satisfied may the project proceed to the next Blueprint.