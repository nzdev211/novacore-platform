# Identity

## Purpose

The Identity bounded context provides immutable, type-safe identifiers for every domain entity in the Novacore Kernel.

## Responsibilities

- Define the language of identity.
- Provide immutable value objects.
- Prevent identity confusion across domain types.

## Public Types

- Identifier
- ConversationId
- ExecutionId
- WorkId
- WorkerId
- RequestId
- TraceId

## Depends On

Nothing (Layer L0)

## Used By

Every bounded context.

## Related Documents

- SPECIFICATION.md
- TEST_PLAN.md