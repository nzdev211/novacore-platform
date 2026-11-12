# Phase 10 — Kernel reconciliation correction

The previous Phase 10 archive was not fully reconciled: legacy `conversation`, `contracts`, `events`, `work_attempt`, and `execution_attempt` source files remained in the Kernel package. This archive corrects that issue by replacing the Kernel `src/` and `tests/` trees with the approved, phase-tested v0.1 implementation from Phase 7.

The approved model uses `Context` (not `Conversation`), `Work` (without legacy attempt/input/constraints/status/outcome objects), and `Execution` (one immutable record containing `id` and `assignment_id`). Runtime orchestration and provider contracts remain outside Kernel.

This is a ZIP snapshot only; it does not change the GitHub repository.

