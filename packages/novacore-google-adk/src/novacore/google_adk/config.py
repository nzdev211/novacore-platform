from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, slots=True)
class GoogleADKConfig:
    app_name: str
    session_backend: Literal["memory", "custom"] = "memory"
    user_id_prefix: str = "novacore-worker"

    def __post_init__(self) -> None:
        if not isinstance(self.app_name, str) or not self.app_name.strip():
            raise ValueError("app_name must be a non-empty string.")
        if self.session_backend not in ("memory", "custom"):
            raise ValueError("session_backend must be 'memory' or 'custom'.")
        if not isinstance(self.user_id_prefix, str) or not self.user_id_prefix.strip():
            raise ValueError("user_id_prefix must be a non-empty string.")

