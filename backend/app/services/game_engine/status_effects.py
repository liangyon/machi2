"""
Status effect definitions and helper functions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ─── Data classes ─────────────────────────────────────────────────────────────


@dataclass
class CombatResult:
    """Result of a single combat turn."""
    player_hp: int
    player_mana: int
    player_status_effects: list[dict]
    enemy_hp: int
    enemy_status_effects: list[dict]
    player_damage_dealt: int
    enemy_damage_dealt: int
    player_action_label: str
    enemy_action_label: str
    player_extra_action: bool
    enemy_extra_action: bool
    player_won: bool       # enemy hp <= 0
    player_died: bool      # player hp <= 0
    xp_gained: int
    gold_gained: int
    narration_context: dict  # passed to LLM in Phase 2


@dataclass
class ExploreResult:
    """Result of a single exploration action."""
    event_type: str          # empty | enemy | chest | shrine | shop | boss
    danger_meter: int
    action_count: int
    enemy: dict | None = None          # populated if event_type == "enemy"
    loot: list[dict] | None = None     # populated if event_type == "chest"
    shop_items: list[dict] | None = None  # populated if event_type == "shop"
    shrine_outcomes: list[str] | None = None  # pre-rolled if event_type == "shrine"


# ─── Status effect metadata ────────────────────────────────────────────────────


def _make_effect(name: str, emoji: str, turns: int, value: int = 0,
                 description: str = "") -> dict:
    return {
        "name": name,
        "emoji": emoji,
        "turnsRemaining": turns,
        "value": value,
        "description": description or name,
    }


EFFECT_META: dict[str, dict] = {
    "burn":       {"emoji": "🔥", "desc": "Fire damage per turn"},
    "bleed":      {"emoji": "🩸", "desc": "Physical damage per turn"},
    "poison":     {"emoji": "☠️",  "desc": "Poison damage per turn"},
    "decay":      {"emoji": "💀", "desc": "Void damage per turn, reduces max HP"},
    "frostbite":  {"emoji": "❄️",  "desc": "Cold damage per turn"},
    "stun":       {"emoji": "⚡", "desc": "Skip turns"},
    "slow":       {"emoji": "🐢", "desc": "Acts every other turn"},
    "silence":    {"emoji": "🔇", "desc": "Cannot cast spells"},
    "root":       {"emoji": "🌿", "desc": "Cannot flee"},
    "confuse":    {"emoji": "🌀", "desc": "Attacks randomly"},
    "fear":       {"emoji": "😱", "desc": "Skips turn, takes bonus damage"},
    "weaken":     {"emoji": "💔", "desc": "Reduced attack"},
    "shatter":    {"emoji": "🛡️",  "desc": "Reduced defense"},
    "drain_mana": {"emoji": "💧", "desc": "Mana drained per turn"},
    "empower":    {"emoji": "⚔️",  "desc": "Increased attack"},
    "fortify":    {"emoji": "🏰", "desc": "Increased defense"},
    "haste":      {"emoji": "💨", "desc": "Increased speed"},
    "lifesteal":  {"emoji": "🧛", "desc": "Heals on damage dealt"},
    "regen":      {"emoji": "💚", "desc": "HP restored per turn"},
    "mana_regen": {"emoji": "🔵", "desc": "Mana restored per turn"},
    "shield":     {"emoji": "🛡️",  "desc": "Absorbs incoming damage"},
    "reflect":    {"emoji": "🪞", "desc": "Reflects incoming attacks"},
    "curse_mark": {"emoji": "🎯", "desc": "Takes increased damage"},
}


# ─── Status effect helpers ────────────────────────────────────────────────────


def apply_effect_to_target(effects: list[dict], effect_name: str,
                            value: int, duration: int) -> list[dict]:
    """Add or refresh a status effect on a target's effect list."""
    meta = EFFECT_META.get(effect_name, {"emoji": "✨", "desc": effect_name})
    # Most effects refresh duration; poison stacks value
    for existing in effects:
        if existing["name"] == effect_name:
            if effect_name == "poison":
                existing["value"] += value
            existing["turnsRemaining"] = max(existing["turnsRemaining"], duration)
            return effects
    effects.append(_make_effect(
        effect_name, meta["emoji"], duration, value, meta["desc"]
    ))
    return effects


def tick_effects(effects: list[dict], target_stats: dict) -> tuple[list[dict], int, list[str]]:
    """
    Tick all status effects on a target.
    Returns (updated_effects, total_dot_damage, log_messages).
    Modifies target_stats in-place for stat-mod effects.
    """
    dot_damage = 0
    messages: list[str] = []
    remaining: list[dict] = []

    for eff in effects:
        name = eff["name"]
        val = eff.get("value", 0)

        # DoT effects
        if name in ("burn", "bleed", "poison", "frostbite"):
            dot_damage += val
            messages.append(f"{eff['emoji']} {name.capitalize()} deals {val} damage")
        elif name == "decay":
            dot_damage += val
            # Also reduce max HP by 1
            target_stats["max_hp"] = max(1, target_stats.get("max_hp", 100) - 1)
            messages.append(f"{eff['emoji']} Decay deals {val} damage and withers max HP")
        elif name == "drain_mana":
            target_stats["mana"] = max(0, target_stats.get("mana", 0) - val)
            messages.append(f"{eff['emoji']} Mana drained by {val}")
        elif name == "regen":
            heal = val
            target_stats["hp"] = min(
                target_stats.get("max_hp", 100),
                target_stats.get("hp", 0) + heal
            )
            messages.append(f"{eff['emoji']} Regenerated {heal} HP")
        elif name == "mana_regen":
            target_stats["mana"] = min(
                target_stats.get("max_mana", 50),
                target_stats.get("mana", 0) + val
            )
            messages.append(f"{eff['emoji']} Restored {val} Mana")

        # Decrement and keep if still active
        eff["turnsRemaining"] -= 1
        if eff["turnsRemaining"] > 0:
            remaining.append(eff)
        else:
            messages.append(f"{eff['emoji']} {name.capitalize()} wore off")

    return remaining, dot_damage, messages


def has_effect(effects: list[dict], name: str) -> bool:
    return any(e["name"] == name for e in effects)


def get_effect_value(effects: list[dict], name: str) -> int:
    for e in effects:
        if e["name"] == name:
            return e.get("value", 0)
    return 0