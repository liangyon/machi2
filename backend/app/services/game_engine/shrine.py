"""
Shrine outcome generation and application logic.
"""

from __future__ import annotations

import copy
import random
from typing import Any


class ShrineEngine:
    """
    Shrine-related game logic.
    All methods are static — no instance state.
    """

    @staticmethod
    def roll_shrine_outcomes() -> list[dict]:
        """
        Pre-roll 3 shrine outcomes (buff / curse / neutral).
        Each outcome has a type and a concrete effect.
        """
        outcomes = [
            # Buffs
            {"type": "buff", "effect": "hp_up_20",      "description": "Your wounds close. Max HP +20."},
            {"type": "buff", "effect": "mana_up_15",     "description": "Arcane energy surges. Max Mana +15."},
            {"type": "buff", "effect": "attack_up_3",    "description": "Your strikes grow sharper. Attack +3."},
            {"type": "buff", "effect": "defense_up_3",   "description": "Your skin hardens. Defense +3."},
            {"type": "buff", "effect": "speed_up_2",     "description": "Time bends to your will. Speed +2."},
            {"type": "buff", "effect": "gold_100",       "description": "Coins rain from the altar. Gold +100."},
            {"type": "buff", "effect": "luck_up_3",      "description": "Fortune smiles upon you. Luck +3."},
            # Curses
            {"type": "curse", "effect": "hp_down_15",    "description": "The shrine drains your vitality. Max HP -15."},
            {"type": "curse", "effect": "mana_down_10",  "description": "Your mana reservoir shrinks. Max Mana -10."},
            {"type": "curse", "effect": "attack_down_2", "description": "Your arms feel heavy. Attack -2."},
            {"type": "curse", "effect": "gold_loss_50",  "description": "The shrine takes its tithe. Gold -50."},
            # Neutral
            {"type": "neutral", "effect": "swap_hp_mana",   "description": "HP and Mana values are swapped."},
            {"type": "neutral", "effect": "full_heal",       "description": "HP fully restored, but Mana halved."},
            {"type": "neutral", "effect": "danger_reset",    "description": "Danger meter resets to 0."},
        ]

        # Pick one buff, one curse, one neutral (or random if not enough)
        buffs   = [o for o in outcomes if o["type"] == "buff"]
        curses  = [o for o in outcomes if o["type"] == "curse"]
        neutral = [o for o in outcomes if o["type"] == "neutral"]

        chosen = [
            random.choice(buffs),
            random.choice(curses),
            random.choice(neutral),
        ]
        random.shuffle(chosen)
        return chosen

    @staticmethod
    def apply_shrine_outcome(state: dict, outcome: dict) -> dict:
        """Apply a shrine outcome to the player state."""
        s = copy.deepcopy(state)
        effect = outcome.get("effect", "")

        if effect == "hp_up_20":
            s["max_hp"] = s.get("max_hp", 100) + 20
            s["hp"] = min(s.get("hp", 100) + 20, s["max_hp"])
        elif effect == "mana_up_15":
            s["max_mana"] = s.get("max_mana", 50) + 15
            s["mana"] = min(s.get("mana", 50) + 15, s["max_mana"])
        elif effect == "attack_up_3":
            s["attack"] = s.get("attack", 10) + 3
        elif effect == "defense_up_3":
            s["defense"] = s.get("defense", 5) + 3
        elif effect == "speed_up_2":
            s["speed"] = s.get("speed", 10) + 2
        elif effect == "gold_100":
            s["gold"] = s.get("gold", 0) + 100
        elif effect == "luck_up_3":
            s["luck"] = s.get("luck", 5) + 3
        elif effect == "hp_down_15":
            s["max_hp"] = max(10, s.get("max_hp", 100) - 15)
            s["hp"] = min(s.get("hp", 100), s["max_hp"])
        elif effect == "mana_down_10":
            s["max_mana"] = max(10, s.get("max_mana", 50) - 10)
            s["mana"] = min(s.get("mana", 50), s["max_mana"])
        elif effect == "attack_down_2":
            s["attack"] = max(1, s.get("attack", 10) - 2)
        elif effect == "gold_loss_50":
            s["gold"] = max(0, s.get("gold", 0) - 50)
        elif effect == "swap_hp_mana":
            old_hp = s.get("hp", 100)
            old_mana = s.get("mana", 50)
            s["hp"] = min(old_mana, s.get("max_hp", 100))
            s["mana"] = min(old_hp, s.get("max_mana", 50))
        elif effect == "full_heal":
            s["hp"] = s.get("max_hp", 100)
            s["mana"] = max(1, s.get("mana", 50) // 2)
        elif effect == "danger_reset":
            s["danger_meter"] = 0

        return s