# Phase 25 — Storyboard Review Context and Asset Preview

## Goal

Extend the Phase 24 review screen to display the storyboard package associated with a review: a creative brief, a flexible structured shot specification, and references to externally stored visual assets.

## Boundary decisions

- No Kernel changes and no new Kernel attributes.
- No binary media is stored in Kernel, Runtime review records, or Firestore review metadata.
- The FastAPI adapter exposes an optional read-only context endpoint.
- The host application composes the context from its persisted workflow/execution output and resource metadata.
- The Next.js application renders the returned presentation data; it does not infer or reconstruct it.

## API contract

`GET /reviews/{review_id}/context`

Returns:
- `review_id`: must match the requested review.
- `brief`: optional creative brief text.
- `shot_spec`: flexible JSON object; keys are presentation labels and values are strings, numbers, booleans, arrays, or objects.
- `assets`: list of `{asset_id, label, media_type, uri, alt_text?}`.

The endpoint is provided by `create_review_context_router(load_review_context, authenticate_reviewer)`. The resolver receives both `review_id` and the authenticated `reviewer_id`. It must enforce review ownership/tenant access and ensure the returned execution belongs to the review. The route validates the response shape and matching review ID.

## Asset URI policy

The API should return HTTPS URLs that are short-lived signed URLs or are protected by the application's normal authorization layer. Do not return private bucket paths, raw storage credentials, or long-lived public links. The browser uses native image/video elements; other assets are shown as external links. Configure CSP `img-src`, `media-src`, and `connect-src` to match the deployment's asset/API hosts.

## UI behavior

- The page attempts to load review metadata and context separately.
- If context is not wired or unavailable, the reviewer can still see the review metadata and make a decision.
- Shot specification fields are rendered dynamically, so the workflow can evolve its output contract without changing Kernel.
- Image and video assets receive previews; other file types receive an open link.

## Host integration example

```python
def load_review_context(*, review_id: str, reviewer_id: str):
    # 1. Load the review and enforce tenant/resource authorization.
    review = review_store.load_review(review_id)
    if review is None:
        return None
    authorize_reviewer(reviewer_id, review)

    # 2. Load the persisted workflow/execution snapshot using the
    #    ActivityId associated with the review. Verify execution_id matches.
    snapshot = workflow_store.load_workflow(review.activity_id)
    execution = find_execution(snapshot, review.execution_id)
    if execution is None:
        return None

    # 3. Map your actual execution output and external resource metadata
    #    to the API contract. Do not assume an output schema that your
    #    worker has not implemented.
    return {
        "review_id": review_id,
        "brief": extract_brief(snapshot),
        "shot_spec": extract_shot_spec(execution.output),
        "assets": resolve_asset_references(execution.output),
    }
```

The helper functions above are host-application responsibilities and illustrative placeholders, not Novacore package APIs.

## Out of scope

Asset upload, image generation, editing, permanent public hosting, asset lifecycle/versioning, automatic regeneration, and a canonical storyboard-shot schema.

