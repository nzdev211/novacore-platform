# Human Review Operations

## Persist a review

Create a `ReviewRecord` with a caller-supplied review ID and `PENDING` status,
then call `HumanReviewService.submit_for_review`.

## Record a decision

Call `HumanReviewService.decide` with the review ID, authenticated reviewer ID,
one of `APPROVED`, `CHANGES_REQUESTED`, or `REJECTED`, optional feedback, and
the decision timestamp.

Only a pending review can be decided. A concurrent or repeated decision is
rejected; reload the review before taking further action.

## Resume behavior

Load the review by ID through `ReviewStore.load_review`. A pending review can
be presented to the reviewer again. A decided review is historical and should
not be overwritten. For a revision, create a new execution and a new review
record after the relevant execution recovery/reconciliation checks.

## Security and storage

Reviewer authentication/authorization is the responsibility of the calling
application. Do not accept reviewer IDs directly from an untrusted client.
Firestore stores review metadata and feedback, not image/video binaries or
large generated assets.

