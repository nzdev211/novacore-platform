# Phase 17 — Firestore Workflow Persistence

## Objective

Implement the Runtime `WorkflowStore` port in the independent `novacore-firestore` adapter. Kernel and provider boundaries remain unchanged.

## Initial persistence

`FirestoreWorkflowStore` persists the initial Creative Studio workflow in one Firestore transaction:

- Request
- Context
- Objective
- Activity
- Planning
- Work
- one or more Contracts
- Assignment

Execution identity is written separately before the worker is invoked. No transaction is held open across an external agent call.

## Storage layout

Each domain type has a top-level collection. Domain identifier values are stored in document payloads and URL-safe Base64 encoded for Firestore document IDs. A SHA-256 fallback is used when an encoded identifier exceeds Firestore's document-ID length limit.

## Evolution after Phase 17

Phase 19 extended the same persistence boundary with `WorkflowSnapshot` and `load_workflow(activity_id)`. The adapter can now rehydrate the persisted Request, Context, Objective, Activity, Planning, Work, Contract, Assignment, and Execution records needed to reopen a Creative Studio workflow.

A missing Activity returns `None`. A workflow with missing required related records or a read failure raises `PersistenceError`. Loading is performed through multiple document reads and collection queries; it is not a cross-collection transactional snapshot.

Execution lifecycle metadata and recovery/idempotency policy were added in later phases and remain Runtime responsibilities. Google ADK session persistence remains separate from business workflow persistence.

## Boundaries

- The adapter imports Kernel domain types and the Runtime `WorkflowStore` protocol; Kernel and Runtime do not import Firestore.
- The Google Cloud SDK is optional and imported lazily.
- Context metadata is recursively mapped to Firestore-native values.
- Worker-directory persistence, ADK session persistence, and provider-side exactly-once execution are not provided by this adapter.

## Tests

Fake-client unit tests cover transaction grouping, mappings, safe document IDs, separate Execution writes, workflow rehydration, missing Activity behavior, and persistence error translation. An opt-in emulator integration test runs when `FIRESTORE_EMULATOR_HOST` is set.

