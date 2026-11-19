# Phase 11 — Creative Studio: First End-to-End Workflow

## 1. Purpose

Define one narrow, end-to-end Creative Studio workflow so Runtime contracts can be derived from a real business operation. This phase defines workflow behavior and boundaries; it does not add fields or lifecycle behavior to Kernel domain objects.

## 2. First use case

**Create and approve one storyboard shot package.** A user provides a creative brief and asks the studio to produce one storyboard shot. The output is a structured shot specification plus a visual asset reference. A human reviews the result and either approves it or requests a revision.

The first implementation should handle one shot per workflow. Multi-shot episodes, batch production, publishing, billing, and collaboration are out of scope.

## 3. Domain mapping

| Domain object | Role in this workflow |
|---|---|
| `Request` | Captures the user's original request in `description`. |
| `Context` | Holds contextual metadata through `ContextAttributes`, such as the creative brief, character continuity notes, visual style, aspect ratio, and relevant resource references. |
| `Objective` | States the intended outcome, e.g. produce an approved storyboard shot package. |
| `Activity` | Groups the effort and references the Request, Context, and Objective. |
| `Planning` | Describes the plan for producing the shot, including the intended stages and dependencies in its description. |
| `Work` | Represents a unit of work within the Activity; for v0.1, one Work represents producing the initial shot package. |
| `Contract` | Describes the expected deliverable and acceptance expectations for that Work. Multiple Contracts may be associated with a Work; v0.1 stores each as a description. |
| `Capability` | Describes a capability needed, such as script drafting, storyboard composition, or image generation. |
| `Worker` | Represents the responsible execution resource: AI agent, human, service, or tool. |
| `Assignment` | Allocates the Work to a Worker. |
| `Execution` | Records an attempt associated with the Assignment. A later revision can be represented by another Execution; no retry/lifecycle fields are added here. |

## 4. Workflow sequence

1. **Receive request.** The inbound adapter receives the user's brief and obtains or assigns a `RequestId`. The Kernel does not generate identifiers.
2. **Establish context.** Create a `Context` with `ContextAttributes` containing only the contextual data needed for this activity. Large files and generated images remain external resources; context stores references/URIs rather than file bytes.
3. **Define outcome.** Create an `Objective` describing the approved shot package.
4. **Create activity.** Create an `Activity` linking the Request, Context, and Objective, initially in `DRAFT`. Activate it when work is authorized.
5. **Plan.** Create a `Planning` record for the Activity and Objective. Its description states the production sequence, for example: interpret brief → draft shot specification → generate visual asset → validate deliverable → human review.
6. **Define work and contract.** Create a `Work` linked to the Activity and optionally the Planning. Create one or more `Contract` records describing the expected shot specification and visual asset deliverable.
7. **Select and assign worker.** Runtime selects a Worker whose capabilities match the work and creates an `Assignment`. Worker selection and capability matching are Runtime responsibilities, not Kernel behavior.
8. **Execute.** Runtime creates an `Execution` for the Assignment and invokes the appropriate worker adapter. Model generation and agent-framework execution remain separate adapter paths.
9. **Validate.** Runtime validates the returned deliverable against the Contract descriptions. Technical validation can be automated; creative quality and continuity require human review in this first workflow.
10. **Human review.** Present the shot package to the user/reviewer. Approval ends this workflow and the Activity can be marked `COMPLETED`. A revision request creates follow-up work/assignment/execution under the same Activity, subject to the approved v0.1 object model and application orchestration.
11. **Persist outcome and references.** Runtime persists domain records and external resource references through the selected persistence adapter.

## 5. Human approval boundary

Human approval is a **Runtime workflow gate**, not a new Kernel entity or field in v0.1. The first workflow must pause before treating the deliverable as approved. The reviewer can approve or request revision. Runtime records the decision in its workflow/persistence layer and resumes orchestration accordingly. Do not add `approval_status`, reviewer fields, or transition methods to Kernel without a separate domain-design decision.

## 6. Responsibility boundaries

| Concern | Owner |
|---|---|
| Immutable domain objects, identifiers, local invariants | Kernel |
| Planning orchestration, worker selection, assignment, execution coordination, review pause/resume | Runtime |
| HTTP request/response and authentication integration | FastAPI adapter |
| Direct text/image model calls | Provider-specific model adapters (e.g. OpenAI, Anthropic) |
| Agent-framework execution | Google ADK adapter |
| File/blob storage and metadata persistence | Firestore/PostgreSQL adapters plus an appropriate resource-storage adapter when selected |
| Human review UI | Creative Studio application/UI |

## 7. Model generation vs agent execution

These are distinct paths. A direct model-generation worker invokes a model provider for a bounded generation task. An agent-execution worker invokes an agent framework that may plan, use tools, and perform multiple steps. Runtime coordinates both through distinct provider-independent contracts; it must not force them into one lowest-common-denominator interface. The exact Python Protocols are deferred to Phase 12.

## 8. Persistence and transaction boundaries

- Persist the initial Request, Context, Objective, Activity, Planning, Work, Contracts, Worker/Capability references, and Assignment as a coherent application operation where the chosen database supports a transaction.
- Persist an Execution record before invoking the worker so an attempt is identifiable even if the provider call fails.
- Persist execution outcome metadata and external resource references after the call. The v0.1 `Execution` object itself contains only `id` and `assignment_id`; outcome metadata belongs to Runtime persistence until a domain change is approved.
- Do not hold a database transaction open during a model/agent call or human review wait.
- Treat provider invocation and persistence as a distributed workflow: use idempotency/correlation at the Runtime boundary; do not claim exactly-once execution.
- Store large generated media in object/blob storage; persist stable resource references and metadata, not binary content in `ContextAttributes`.

## 9. Failure and revision behavior

- If worker invocation fails, retain the Execution record and Runtime-owned failure details; a subsequent attempt receives a new Execution identity.
- If validation fails, Runtime may request a new attempt or revision. The choice is orchestration policy, not a Kernel status transition.
- If human review requests changes, preserve the previous output as a versioned external resource and create follow-up work/assignment/execution as appropriate.
- If persistence fails after a provider call, Runtime must reconcile using correlation/idempotency data and the persisted Execution identity; do not blindly repeat a potentially costly generation.

## 10. Explicit v0.1 non-goals

No new Kernel fields or entities for approval, deliverable files, prompts, model parameters, execution status/result, retries, event sourcing, worker endpoints, worker health, or resource storage. No aggregate root is introduced. No provider SDK is imported into Kernel.

## 11. Acceptance criteria for this workflow

- A user request can be traced through Activity, Planning, Work, Contract, Assignment, and one or more Executions.
- The selected Worker is compatible with the required Capability set according to Runtime policy.
- The output includes a shot specification and a resource reference for its visual asset.
- The workflow cannot mark the Activity completed before human approval.
- A revision creates a distinguishable subsequent attempt without mutating immutable Kernel objects.
- Kernel remains dependency-free and unchanged by workflow orchestration.

## 12. Decisions still required before implementation

1. Exact shot-package schema and acceptance checklist (Creative Studio product decision).
2. Which worker is used for each stage: direct model generation, Google ADK agent, deterministic service, or human.
3. Whether resource storage is a separate adapter/package and which provider is selected.
4. Runtime persistence model for workflow state, attempt outcome, review decisions, and idempotency keys.
5. Whether a revision reuses the same Work with a new Assignment/Execution or creates a new Work. The current Kernel allows either structurally; product semantics must choose.

