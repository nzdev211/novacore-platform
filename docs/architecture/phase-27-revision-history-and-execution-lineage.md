# Phase 27 — Revision History and Execution Lineage

## Goal

Expose the complete revision chain for a storyboard Work from any review in that chain, and display it in the Creative Studio review page.

## Architecture boundaries

- No Kernel schema changes and no new Kernel domain entities.
- Execution records remain immutable historical attempts; a revision creates a new Execution.
- Review records remain individual terminal/pending decisions; a revision creates a new ReviewRecord.
- Activity and Work identify the scope of the storyboard item whose versions are being compared.
- The lineage is a Runtime/application read projection assembled by the host callback. It is not a new Kernel aggregate.
- The callback must authorize access to the requested review and every record returned, including tenant/resource boundaries.

## API

`GET /reviews/{review_id}/history`

The route injects the authenticated reviewer identity and delegates to `load_revision_history(review_id, reviewer_id)`. The callback returns:

- `activity_id` and `work_id` for the lineage scope;
- `entries`, oldest first, each with `review_id`, `execution_id`, `activity_id`, `work_id`, `review_status`, `created_at`, and optional `execution_status`, `source_review_id`, and `feedback`.

The route validates that the requested review is in the chain, review and execution IDs are unique, and every entry belongs to the same Activity and Work. The host callback is responsible for ordering entries chronologically and verifying the parent/revision relationships against persisted data.

## Persistence guidance for host integration

Phase 26 returns `source_review_id` when a revision is created. The host application should persist that relationship alongside its revision/review workflow metadata (or in an equivalent application-level lineage record). It should not add this as a Kernel field. To assemble history for any review, follow the persisted source-review relationship to the root, then collect its descendants and associated execution lifecycle records. Detect cycles, missing parents, duplicate execution links, and cross-Activity/Work references; fail closed rather than returning a misleading chain.

The callback should return only the lineage entries authorized for the authenticated reviewer. Asset URLs are not returned by this endpoint; each review continues to obtain its exact execution's assets from the Phase 25 `/context` endpoint.

## UI behavior

The review page requests history independently from the review and storyboard context. It displays versions oldest-first with review status, execution ID/status, creation time, and reviewer feedback. If history is unavailable, the review and decision workflow remain usable and an explanatory message is shown.

## Out of scope

- Persisting revision lineage in a specific database schema; the host owns that mapping.
- New Kernel entities or attributes.
- Asset binary/version storage or asset URL delivery.
- A full episode-wide timeline across multiple Work items.
- Editing or deleting prior execution/review records.

