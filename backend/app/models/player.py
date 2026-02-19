from pydantic import BaseModel
from typing import Optional
import json


class Player(BaseModel):
    oauth_id: str
    username: str
    provider: str  # google | github | password
    email: Optional[str] = None
    password_hash: Optional[str] = None
    auth_method: str = "oauth"  # "oauth" | "password"
    linked_provider: Optional[str] = None  # OAuth provider linked to a password account via merge
    legacy_spellbook: list = []
    grimoire_count: int = 0
    is_banned: bool = False
    created_at: Optional[str] = None
    last_login: Optional[str] = None

    @classmethod
    def from_row(cls, row) -> "Player":
        data = dict(row)
        data["legacy_spellbook"] = json.loads(data.get("legacy_spellbook", "[]"))
        data["is_banned"] = bool(data.get("is_banned", 0))
        return cls(**data)


class PlayerProfile(BaseModel):
    username: str
    provider: str
    email: Optional[str] = None
    auth_method: str
    legacy_spellbook: list
    grimoire_count: int
