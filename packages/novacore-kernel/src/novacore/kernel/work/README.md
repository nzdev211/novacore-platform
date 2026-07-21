# Work

## Purpose
Defines the concept of "Work" within the kernel. Represents tasks or jobs that need to be executed, tracked, and completed.

## Responsibilities
- Encapsulate inputs, outputs, and constraints of a unit of work.
- Track work status and lifecycle (created, in-progress, completed, failed).
- Manage attempts and retries for work execution.
- Provide a consistent interface for higher-level modules to interact with work entities.

## Public Types
- Work
- WorkInput
- WorkOutput
- WorkConstraints
- WorkStatus
- WorkAttempt

## Depends On
- Execution
- Identity
- Contracts

## Used By
- Worker
- Events
- Result

## Rules
- Work must always have a valid input and constraints before execution.
- Status transitions must follow a strict lifecycle (Created → In Progress → Completed/Failed).
- Attempts are logged and retried only within defined constraints.
Work
Represents: A unit of business intent.
Invariants:
Must declare at least one required capability.
Must have exactly one identity.
Must never mutate its business intent after creation.


## Future Evolution
- Support for distributed work orchestration.
- Enhanced constraint definitions (time limits, resource quotas).
- Integration with error handling for automatic recovery.
- Advanced scheduling and prioritization mechanisms.
