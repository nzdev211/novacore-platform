# Revision orchestration — operations

## Composition

Construct `RevisionWorkflowService` with four application adapters:
`RevisionSourceStore`, `RevisionExecutionPort`, `RevisionRecordStore`, and
`RevisionReviewCreator`. Inject its `create_revision` method into
`create_revision_router`.

The source loader must authorize the creator for the review and every linked
record. Never trust a client-supplied execution, Activity, Work, or reviewer ID.

## Execution input

Build the new agent input from:
- the original creative brief and source execution input;
- the source execution output (for continuity);
- the source review feedback;
- optional additional instructions.

Do not simply append feedback to an unbounded prompt. The host should apply its
normal prompt/versioning and input-size policies.

## Failure handling

- Source review not found: return 404.
- Creator not authorized: return 403.
- Source status other than CHANGES_REQUESTED: return 409.
- Existing completed idempotency key: return the same revision result.
- Existing in-progress key: return a conflict/in-progress response; reconcile it.
- Failed execution: persist FAILED; do not create a review.
- Uncertain RUNNING execution: reconcile; do not blindly retry.
- Successful execution but missing review: finish review creation from the
  stored output; do not invoke the agent again.

## Production gate

Before enabling the endpoint, verify that the revision key reservation is
atomic across concurrent requests and that all four adapters are covered by
integration tests against the actual Firestore schema.

