# Dependency Graph

**Version:** 0.1.0

**Status:** Draft

---

# Purpose

This document defines the dependency architecture of the Novacore Kernel.

The dependency graph guarantees that business concepts remain stable, independent, and reusable.

Every bounded context belongs to exactly one dependency layer.

Dependencies always point toward lower layers.

Circular dependencies are never permitted.

---

# Philosophy

The Novacore Kernel follows the Dependency Rule.

> Source code dependencies always point toward more fundamental business concepts.

Higher layers understand lower layers.

Lower layers never understand higher layers.

This allows business language to remain stable while execution technology evolves.

---

# Dependency Layers

```
L0

Identity
```

↓

```
L1

Capability
```

↓

```
L2

Context

Objective
```

↓

```
L3

Planning
```

↓

```
L4

Work
```

↓

```
L5

Worker
```

↓

```
L6

Contract
```

↓

```
L7

Execution
```

↓

```
L8

Event
```

---

# Layer Responsibilities

## Layer 0

Identity

Mission

Provide immutable identities for every Kernel concept.

Depends On

Nothing.

---

## Layer 1

Capability

Mission

Represent business abilities.

Depends On

Identity

---

## Layer 2

Context

Mission

Represent available business information.

Depends On

Identity

---

Objective

Mission

Represent desired business outcomes.

Depends On

Identity

Context

Capability

---

## Layer 3

Planning

Mission

Discover executable decomposition of Objectives.

Depends On

Identity

Capability

Context

Objective

---

## Layer 4

Work

Mission

Represent executable business objectives.

Depends On

Identity

Capability

Context

Objective

Planning

---

## Layer 5

Worker

Mission

Represent execution providers.

Depends On

Identity

Capability

Work

---

## Layer 6

Contract

Mission

Represent agreements between Work and Worker.

Depends On

Identity

Capability

Work

Worker

---

## Layer 7

Execution

Mission

Represent runtime occurrences.

Depends On

Identity

Capability

Work

Worker

Contract

---

## Layer 8

Event

Mission

Represent immutable execution history.

Depends On

Every lower layer.

Events never introduce upward dependencies.

---

# Dependency Matrix

| Context | Allowed Dependencies |
|----------|----------------------|
| Identity | — |
| Capability | Identity |
| Context | Identity |
| Objective | Identity, Context, Capability |
| Planning | Identity, Capability, Context, Objective |
| Work | Identity, Capability, Context, Objective, Planning |
| Worker | Identity, Capability, Work |
| Contract | Identity, Capability, Work, Worker |
| Execution | Identity, Capability, Work, Worker, Contract |
| Event | All lower layers |

---

# Forbidden Dependencies

Identity must never depend on anything.

Capability must never depend on:

- Work
- Worker
- Execution
- Runtime

Planning must never depend on:

- Worker
- Execution
- Runtime

Work must never depend on:

- Worker
- Execution
- Runtime

Worker must never depend on:

- Execution
- Runtime

Execution must never depend on:

- Event

No bounded context may depend on:

- Google ADK
- FastAPI
- Firestore
- PostgreSQL
- HTTP
- Docker
- Kubernetes

Infrastructure belongs outside the Kernel.

---

# Runtime Relationship

The Runtime is **not** part of the dependency graph.

The Runtime consumes the Kernel.

```
           Runtime

              │

              ▼

Identity

↓

Capability

↓

Context

↓

Objective

↓

Planning

↓

Work

↓

Worker

↓

Contract

↓

Execution

↓

Event
```

The Runtime depends on the Kernel.

The Kernel never depends on the Runtime.

---

# Circular Dependency Rule

Circular dependencies are forbidden.

Example

```
Work

↓

Worker

↓

Execution

↓

Work
```

Invalid.

---

Valid

```
Planning

↓

Work

↓

Worker

↓

Execution

↓

Event
```

---

# Architectural Goals

The dependency graph exists to achieve:

- Stable business language
- Technology independence
- High cohesion
- Low coupling
- Independent evolution
- Testability
- Reusability

---

# Dependency Principles

1. Dependencies always point downward.

2. Lower layers never know higher layers.

3. Runtime depends on Kernel.

4. Infrastructure depends on Runtime.

5. Business language never depends on technology.

6. Circular dependencies are forbidden.

7. Every bounded context belongs to exactly one dependency layer.

8. Every dependency must strengthen—not weaken—the ubiquitous language.

---

# Future Evolution

Future bounded contexts must integrate into the dependency graph without violating existing dependency rules.

New layers may be introduced only when:

- responsibilities cannot be expressed within existing layers,
- dependency direction remains preserved,
- business language becomes clearer.

Adding a new layer requires an Architectural Decision Record (ADR).

---

# Exit Criteria

This dependency graph is considered stable when:

- every bounded context has an assigned dependency layer,
- dependency rules are documented,
- forbidden dependencies are documented,
- architecture tests verify dependency direction,
- no circular dependencies exist.

Breaking these rules requires approval through a Novacore Change Request (NCR).
