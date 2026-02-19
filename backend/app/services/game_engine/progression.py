"""
Progression and shop generation logic.
"""

from __future__ import annotations

import copy
import random
from typing import Any

from app.services.game_engine.constants import XP_CURVE
from app.data.ingredients import (
    get_floor_loot_pool,
    INGREDIENT_BY_ID,
    CONSUMABLES,
    EQUIPMENT_BY_FLOOR,
    INGREDIENT_BASE_PRICES,
)


class ProgressionEngine:
    """
    Progression-related game logic.
    All methods are static — no instance state.
    """

    # ── Progression ───────────────────────────────────────────────────────────

    @staticmethod
    def check_level_up(state: dict) -> tuple[dict, bool]:
        """
        Check if player has enough XP to level up.
        Returns (updated_state, leveled_up).
        Stat point allocation is handled separately.
        """
        s = copy.deepcopy(state)
        level = s.get("level", 1)
        xp = s.get("xp", 0)

        if level >= len(XP_CURVE):
            return s, False

        threshold = XP_CURVE[level]  # XP needed to reach next level
        if xp >= threshold:
            s["level"] = level + 1
            s["unspent_stat_points"] = s.get("unspent_stat_points", 0) + 3
            # Small HP/mana bonus on level up
            s["max_hp"] = s.get("max_hp", 100) + 5
            s["hp"] = min(s["hp"] + 5, s["max_hp"])
            s["max_mana"] = s.get("max_mana", 50) + 3
            return s, True
        return s, False

    @staticmethod
    def generate_shop_inventory(floor: int) -> list[dict]:
        """
        Generate shop inventory: 2 ingredients, 2 consumables, 1-2 equipment.
        Prices: base_price * floor_multiplier.
        """
        items: list[dict] = []
        floor_mult = 1 + (floor - 1) * 0.2

        # 2 ingredients
        pool = get_floor_loot_pool(floor, danger_tier=2)
        if pool:
            ids, weights = zip(*pool)
            chosen_ids = random.choices(ids, weights=weights, k=2)
            for ing_id in chosen_ids:
                ing = INGREDIENT_BY_ID.get(ing_id)
                if ing:
                    base = INGREDIENT_BASE_PRICES.get(ing["tier"], 30)
                    items.append({
                        "id": ing_id,
                        "name": ing["name"],
                        "type": "ingredient",
                        "tier": ing["tier"],
                        "price": int(base * floor_mult),
                        "ingredient_id": ing_id,
                        "effect": None,
                    })

        # 2 consumables
        chosen_consumables = random.sample(CONSUMABLES, min(2, len(CONSUMABLES)))
        for c in chosen_consumables:
            item = copy.deepcopy(c)
            base = INGREDIENT_BASE_PRICES.get(c["tier"], 30)
            item["price"] = int(base * floor_mult)
            items.append(item)

        # 1-2 equipment
        equip_pool = EQUIPMENT_BY_FLOOR.get(floor, EQUIPMENT_BY_FLOOR.get(1, []))
        count = random.randint(1, 2)
        chosen_equip = random.sample(equip_pool, min(count, len(equip_pool)))
        for eq in chosen_equip:
            item = copy.deepcopy(eq)
            item["price"] = int(eq.get("price", 60) * floor_mult)
            items.append(item)

        return items