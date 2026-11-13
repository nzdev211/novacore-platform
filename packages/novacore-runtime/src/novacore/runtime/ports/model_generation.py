from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class ModelGenerationRequest:
    """Provider-neutral input for one bounded direct-generation operation."""

    prompt: str
    options: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.prompt, str):
            raise TypeError("prompt must be a string.")
        if not self.prompt.strip():
            raise ValueError("prompt cannot be empty or whitespace only.")
        if not isinstance(self.options, Mapping):
            raise TypeError("options must be a mapping.")


@dataclass(frozen=True, slots=True)
class ModelGenerationResponse:
    """Provider-neutral generated content and optional trace metadata."""

    content: str
    provider: str
    model: str
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("content", "provider", "model"):
            value = getattr(self, name)
            if not isinstance(value, str):
                raise TypeError(f"{name} must be a string.")
            if not value.strip():
                raise ValueError(f"{name} cannot be empty or whitespace only.")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping.")


@runtime_checkable
class ModelGenerator(Protocol):
    """Port for direct model APIs; not for agent-framework runtimes."""

    def generate(self, request: ModelGenerationRequest) -> ModelGenerationResponse:
        """Generate one bounded response or raise an adapter-defined exception."""
        ...

