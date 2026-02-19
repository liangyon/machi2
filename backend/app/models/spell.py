"""
Database models for spells and grimoire entries.
"""

from pydantic import BaseModel
from typing import Optional
import json


class SpellStats(BaseModel):
    damage: int = 0
    mana_cost: int = 0
    cooldown: int = 0
    damage_type: str = "arcane"


class GrimoireEntry(BaseModel):
    ingredient_key: str
    variant_index: int = 0
    spell_name: str
    flavor_text: Optional[str] = None
    stats: SpellStats = SpellStats()
    effects: list = []
    ingredient_tiers: dict = {}
    luck_threshold: int = 0
    discovered_by: Optional[str] = None
    discovered_at: Optional[str] = None

    @classmethod
    def from_row(cls, row) -> "GrimoireEntry":
        data = dict(row)
        data["stats"] = SpellStats(**json.loads(data.pop("stats_json", "{}")))
        data["effects"] = json.loads(data.pop("effects_json", "[]"))
        data["ingredient_tiers"] = json.loads(data.pop("ingredient_tiers", "{}"))
        return cls(**data)