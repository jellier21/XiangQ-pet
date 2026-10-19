"""Authentication profile models."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class AuthProfile:
    """The user identity returned by the registration endpoint."""

    name: str
    mark: bool
    uuid: str

    @classmethod
    def from_mapping(cls, payload: dict[str, Any], name: str) -> "AuthProfile":
        """Build an auth profile from an API response object."""
        response = payload.get("data") if isinstance(payload.get("data"), dict) else payload
        uuid = response.get("uuid")
        mark = response.get("mark")
        if not isinstance(uuid, str) or not uuid.strip():
            raise ValueError("注册接口响应中缺少 uuid")
        if not isinstance(mark, bool):
            raise ValueError("注册接口响应中缺少有效的 mark")
        return cls(name=name, mark=mark, uuid=uuid)

    def to_mapping(self) -> dict[str, object]:
        """Return the persisted auth.json representation."""
        return {
            "name": self.name,
            "mark": self.mark,
            "uuid": self.uuid,
        }
