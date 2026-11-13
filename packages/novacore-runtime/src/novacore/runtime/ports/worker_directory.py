from __future__ import annotations

from typing import Protocol, runtime_checkable

from novacore.kernel.capability import Capability
from novacore.kernel.identity import CapabilityId
from novacore.kernel.worker import Worker


@runtime_checkable
class WorkerDirectory(Protocol):
    """Read-only worker/capability discovery port for Runtime assignment policy."""

    def find_workers_with_capabilities(
        self,
        required_capability_ids: frozenset[CapabilityId],
    ) -> tuple[Worker, ...]:
        """Return workers satisfying all requested capabilities."""
        ...

    def get_capabilities(
        self,
        capability_ids: tuple[CapabilityId, ...],
    ) -> tuple[Capability, ...]:
        """Resolve capability references for policy and validation."""
        ...

