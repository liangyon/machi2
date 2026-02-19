"""
Exploration and event generation logic.
"""

from __future__ import annotations

import copy
import random
from typing import Any

from app.services.game_engine.constants import (
    DANGER_PER_ACTION,
    DANGER_EXTRA_PER_OVERACTION,
    ACTION_POOL_BASE,
)
from app.data.enemies import ENEMIES_BY_FLOOR, MINI_BOSSES, FINAL_BOSS, EnemyDef
from app.data.ingredients import (
    get_floor_loot_pool,
    INGREDIENT_BY_ID,
)


class GameEngine:
    """
    Exploration-related game logic.
    All methods are static — no instance state.
    """

    # ── Exploration ───────────────────────────────────────────────────────────

    @staticmethod
    def _danger_tier(danger_meter: int) -> int:
        """Convert danger_meter (0-100) to tier 1-4."""
        if danger_meter <= 30:
            return 1
        elif danger_meter <= 60:
            return 2
        elif danger_meter <= 85:
            return 3
        return 4

    @staticmethod
    def explore_action(state: dict) -> tuple[dict, str]:
        """
        Increment action_count, update danger_meter, roll event_type.
        Returns (updated_state, event_type).
        """
        s = copy.deepcopy(state)

        action_pool = s.get("action_pool", ACTION_POOL_BASE)
        action_count = s.get("action_count", 0) + 1
        danger_meter = s.get("danger_meter", 0)
        floor = s.get("floor", 1)

        # Danger escalation
        if action_count > action_pool:
            danger_meter = min(100, danger_meter + DANGER_EXTRA_PER_OVERACTION)
        else:
            danger_meter = min(100, danger_meter + DANGER_PER_ACTION)

        s["action_count"] = action_count
        s["danger_meter"] = danger_meter

        danger_tier = GameEngine._danger_tier(danger_meter)
        event_type = GameEngine._roll_event(floor, danger_tier)

        return s, event_type

    @staticmethod
    def _roll_event(floor: int, danger_tier: int) -> str:
        """
        Weighted event table adjusted by floor and danger tier.
        Higher danger → more enemies, fewer empty rooms.
        """
        # Base weights: empty, enemy, chest, shrine, shop
        base = {
            "empty":  max(5, 35 - danger_tier * 8),
            "enemy":  20 + danger_tier * 10,
            "chest":  15,
            "shrine": 10,
            "shop":   10,
        }
        # Floor 1 has no shop until action 3+
        if floor == 1:
            base["shop"] = max(0, base["shop"] - 5)

        pool = [(k, v) for k, v in base.items() if v > 0]
        total = sum(v for _, v in pool)
        roll = random.randint(1, total)
        cumulative = 0
        for event, weight in pool:
            cumulative += weight
            if roll <= cumulative:
                return event
        return "empty"

    @staticmethod
    def roll_loot(floor: int, danger_tier: int, count: int = 2) -> list[dict]:
        """
        Roll `count` ingredients from the floor loot pool.
        Returns list of {id, name, tier, quantity}.
        """
        pool = get_floor_loot_pool(floor, danger_tier)
        if not pool:
            return []

        ids, weights = zip(*pool)
        chosen_ids = random.choices(ids, weights=weights, k=count)

        result: list[dict] = []
        seen: dict[str, dict] = {}
        for ing_id in chosen_ids:
            ing = INGREDIENT_BY_ID.get(ing_id)
            if not ing:
                continue
            if ing_id in seen:
                seen[ing_id]["quantity"] += 1
            else:
                item = {
                    "id": ing_id,
                    "name": ing["name"],
                    "tier": ing["tier"],
                    "quantity": 1,
                    "type": "ingredient",
                }
                seen[ing_id] = item
                result.append(item)
        return result

    @staticmethod
    def roll_enemy(floor: int) -> dict:
        """Pick a random enemy for the given floor and return a combat-ready dict."""
        enemies = ENEMIES_BY_FLOOR.get(floor, [])
        if not enemies:
            # Floor 8 has no regular enemies — return final boss
            e = dict(FINAL_BOSS)
            e["max_hp"] = e["hp"]
            e["active_status_effects"] = []
            return e
        chosen = random.choice(enemies)
        e = dict(chosen)
        e["max_hp"] = e["hp"]
        e["active_status_effects"] = []
        return e