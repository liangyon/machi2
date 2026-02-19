"""
Database models for runs.
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
import json
import uuid


class GameState(BaseModel):
    hp: int = 100
    max_hp: int = 100
    mana: int = 50
    max_mana: int = 50
    speed: int = 10
    attack: int = 10
    defense: int = 5
    luck: int = 5
    gold: int = 0
    floor: int = 1
    danger_meter: int = 0
    action_count: int = 0
    xp: int = 0
    level: int = 1
    inventory: list = []
    spell_collection: list = []
    equipment: dict = {}
    active_status_effects: list = []
    # Phase 1 additions
    arcane_affinity: int = 5
    strength: int = 10
    action_pool: int = 12
    unspent_stat_points: int = 0
    current_enemy: Optional[dict] = None
    shop_inventory: list = []
    rolled_shrine_outcomes: list = []
    ingredient_inventory: list = []
    consumables: list = []
    kills: int = 0
    cause_of_death: Optional[str] = None


class Run(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    player_id: str
    player_class: str
    state_json: GameState = Field(default_factory=GameState)
    floor: int = 1
    status: Literal["active", "dead", "victory"] = "active"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @classmethod
    def from_row(cls, row) -> "Run":
        data = dict(row)
        state = json.loads(data.pop("state_json", "{}"))
        data["state_json"] = GameState(**state) if state else GameState()
        data["player_class"] = data.pop("class", "warrior")
        return cls(**data)