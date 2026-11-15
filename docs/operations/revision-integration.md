# Revision Integration Operations

Compose the Phase 30 components with the existing stores:

```python
source_store = FirestoreRevisionSourceStore(
    review_store=review_store,
    workflow_store=workflow_store,
    authorize=authorize_review_resource,
    load_execution_input=load_original_execution_input,
)
review_creator = StoreRevisionReviewCreator(
    review_store=review_store,
    create_review_id=review_id_factory,
)
execution_port = CallbackRevisionExecutionPort(execute_revision_with_runtime)
service = RevisionWorkflowService(
    source_store=source_store,
    execution_port=execution_port,
    revision_store=revision_record_store,
    review_creator=review_creator,
)
```

The names above are illustrative host application functions, not built-in Novacore functions. `execute_revision_with_runtime` must call the established Runtime execution lifecycle, allocate a fresh Execution ID outside the Kernel, preserve the original Assignment/Work relationship, and forward the idempotency key. `load_original_execution_input` must resolve the exact source execution's original input. `authorize_review_resource` must enforce tenant and resource-level access, not merely authentication.

Do not return signed asset URLs from this adapter. Asset access remains the responsibility of the Phase 25 review-context resolver.

