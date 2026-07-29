# Novacore Kernel Language

The Novacore Kernel is built around a ubiquitous language.

Every bounded context owns exactly one business concept and answers exactly one business question.

---

## Identity

**Question**

Who am I?

**Mission**

Provide immutable, globally unique identities for every Kernel entity.

---

## Capability

**Question**

What can be done?

**Mission**

Represent reusable business abilities independent of implementation.

---

## Context

**Question**

What information is available?

**Mission**

Represent all information known about a business request before planning.

Context may originate from:

- Human conversations
- REST APIs
- CLI
- Scheduled jobs
- Webhooks
- Event streams
- Other systems

Context is the source of business understanding.

---

## Objective

**Question**

What outcome is desired?

**Mission**

Represent the desired business outcome derived from Context.

Objectives are not executable.

Objectives are transformed into executable Work by the Planning bounded context.

---

## Planning

**Question**

How should the Objective be decomposed?

**Mission**

Discover the optimal executable decomposition of an Objective.

Planning owns:

- Planner
- Work Graph
- Planning Strategy
- Planning Policy
- Optimization
- Human Approval
- Cost Estimation
- Parallelization
- Dependency Analysis
- Risk Analysis

Planning never performs execution.

---

## Work

**Question**

What must be executed?

**Mission**

Represent the smallest independently executable business objective.

Planning creates Work.

Execution consumes Work.

Work remains immutable.

---

## Worker

**Question**

Who can execute it?

**Mission**

Represent an execution provider capable of satisfying one or more Capabilities.

Workers never own business intent.

---

## Contract

**Question**

What agreement governs execution?

**Mission**

Represent the agreement between Work requirements and Worker capabilities.

Contracts enable compatibility without coupling.

---

## Execution

**Question**

What is happening?

**Mission**

Represent one runtime occurrence of executing Work.

Execution owns runtime state.

Execution never changes Work.

---

## Event

**Question**

What changed?

**Mission**

Represent immutable records of business and runtime events.

Events describe history.

Events never modify business definitions.
