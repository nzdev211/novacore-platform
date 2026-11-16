# Phase 36 — ADK Firestore Session Persistence and Recovery

## Goal

Prove that Google ADK conversation state survives recreation of the ADK Runner
and `GoogleADKAgentExecutor`, using the official ADK `FirestoreSessionService`.

## Boundary decisions

- `novacore-google-adk` remains the provider/framework adapter.
- Google ADK owns its session and event history through
  `FirestoreSessionService`.
- Novacore `FirestoreWorkflowStore` continues to own workflow and execution
  records; `FirestoreReviewStore` continues to own human-review records.
- No Kernel domain object or Runtime port is added or changed.
- The ADK session key remains derived from `app_name`, worker-specific `user_id`,
  and `execution_id` (used as `session_id`). Reconstructing an executor with the
  same values therefore addresses the same persisted ADK session.

## What this phase adds

An opt-in live integration test creates an ADK Firestore session, sends a phrase
for the agent to remember, constructs a fresh executor and official Firestore
session service, then asks the agent to recall the phrase. This checks that the
second Runner reads the conversation history persisted by the first Runner.

## Recovery semantics and limitations

This is conversation-session recovery, not automatic re-execution of a
Novacore execution. The test deliberately reuses the same `execution_id` to
address the same ADK session. It does not authorize rerunning a provider call
whose outcome is uncertain. Novacore Phase 21 execution recovery rules remain
unchanged: a RUNNING execution is uncertain and requires reconciliation; a
SUCCEEDED execution reuses its stored result; idempotency does not promise
exactly-once provider execution.

A persisted ADK session does not replace Novacore's execution output, lifecycle,
idempotency reservation, or review persistence. Those records remain in their
existing Novacore stores.

## Test scope

- Real Google ADK `Agent` and Gemini model call.
- Official ADK `FirestoreSessionService` backed by Firestore Emulator.
- Fresh executor/Runner between the remember and recall turns.
- Same app, worker identity, and execution/session ID across recreation.

Not covered: production IAM/security rules, live Firestore service, ADK session
TTL/cleanup policy, ADK Firestore session service with a real cloud project, or
exactly-once model invocation.

