"""Read and persist the local desktop pet authentication profile."""

import json
from pathlib import Path
from typing import Any

from app.models.auth import AuthProfile


class AuthStore:
    """Manage the JSON auth file used to detect first launch."""

    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path

    def load(self) -> AuthProfile | None:
        """Return a valid saved profile, or None for a first launch."""
        if not self.file_path.is_file() or self.file_path.stat().st_size == 0:
            return None

        try:
            payload: Any = json.loads(self.file_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

        if not isinstance(payload, dict):
            return None

        name = payload.get("name")
        mark = payload.get("mark")
        uuid = payload.get("uuid")
        if not isinstance(name, str) or not name.strip():
            return None
        if not isinstance(mark, bool) or not isinstance(uuid, str) or not uuid.strip():
            return None
        return AuthProfile(name=name, mark=mark, uuid=uuid)

    def save(self, profile: AuthProfile) -> None:
        """Persist the profile using UTF-8 and stable readable formatting."""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.file_path.with_suffix(".tmp")
        temporary_path.write_text(
            json.dumps(profile.to_mapping(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        temporary_path.replace(self.file_path)
