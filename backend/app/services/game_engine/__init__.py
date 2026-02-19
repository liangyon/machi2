"""
Game Logic Engine — pure Python, no LLM.

This package re-exports the GameEngine class for backward compatibility.
All logic is split into focused submodules.
"""

from app.services.game_engine.constants import (
    HEAVY_ATTACK_MULTIPLIER,
    DEFEND_DAMAGE_REDUCTION,
    EXTRA_ACTION_SPEED_RATIO,
    BASE_MANA_REGEN,
    DANGER_PER_ACTION,
    DANGER_EXTRA_PER_OVERACTION,
    ACTION_POOL_BASE,
    XP_CURVE,
)
from app.services.game_engine.status_effects import (
    CombatResult,
    ExploreResult,
    EFFECT_META,
    apply_effect_to_target,
    tick_effects,
    has_effect,
    get_effect_value,
)
from app.services.game_engine.combat import GameEngine

__all__ = [
    # Constants
    "HEAVY_ATTACK_MULTIPLIER",
    "DEFEND_DAMAGE_REDUCTION",
    "EXTRA_ACTION_SPEED_RATIO",
    "BASE_MANA_REGEN",
    "DANGER_PER_ACTION",
    "DANGER_EXTRA_PER_OVERACTION",
    "ACTION_POOL_BASE",
    "XP_CURVE",
    # Data classes
    "CombatResult",
    "ExploreResult",
    # Status effects
    "EFFECT_META",
    "apply_effect_to_target",
    "tick_effects",
    "has_effect",
    "get_effect_value",
    # Main engine
    "GameEngine",
]