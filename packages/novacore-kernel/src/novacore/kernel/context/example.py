from novacore.kernel.context import Context, ContextAttributes
from novacore.kernel.identity import ContextId


context = Context(
    id=ContextId("context-001"),
    attributes=ContextAttributes(
        values={
            "title": "Creative Studio",
            "domain": "Marketing",
            "language": "English",
            "preferences": {
                "tone": "professional",
                "style": "cinematic",
            },
            "tags": ["research", "copywriting", "design"],
        }
    ),
)
