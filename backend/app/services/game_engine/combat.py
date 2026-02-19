"""
Combat resolution logic.
"""

from __future__ import annotations

import copy
import random
from typing import Any

from app.services.game_engine.constants import (
    HEAVY_ATTACK_MULTIPLIER,
    DEFEND_DAMAGE_REDUCTION,
    EXTRA_ACTION_SPEED_RATIO,
    BASE_MANA_REGEN,
)
from app.services.game_engine.status_effects import (
    CombatResult,
    EFFECT_META,
    apply_effect_to_target,
    tick_effects,
    has_effect,
    get_effect_value,
)
from app.services.game_engine.exploration import GameEngine as ExplorationEngine


class GameEngine:
    """
    Pure-Python game logic engine.
    All methods are static — no instance state.
    """

    # ── Combat ────────────────────────────────────────────────────────────────

    @staticmethod
    def calculate_damage(
        attacker_attack: int,
        defender_defense: int,
        spell_stats: dict | None = None,
        arcane_affinity: int = 0,
        is_heavy: bool = False,
    ) -> int:
        """
        base = attacker_attack - defender_defense (min 1)
        heavy attack: multiply by HEAVY_ATTACK_MULTIPLIER
        spell: base = spell.damage * (1 + arcane_affinity/100)
        """
        if spell_stats:
            base = spell_stats.get("damage", 10) * (1 + arcane_affinity / 100)
        else:
            base = max(1, attacker_attack - defender_defense)
            if is_heavy:
                base = base * HEAVY_ATTACK_MULTIPLIER
        return max(1, int(base))

    @staticmethod
    def pick_enemy_action(enemy: dict, enemy_hp_pct: float) -> dict:
        """
        Weighted random from enemy's action_table filtered by hp_bracket.
        hp_bracket: "high" = above 50%, "low" = below 50%, "any" = always eligible.
        """
        bracket = "high" if enemy_hp_pct >= 0.5 else "low"
        table = enemy.get("action_table", [])
        eligible = [
            a for a in table
            if a.get("hp_bracket", "any") in (bracket, "any")
        ]
        if not eligible:
            eligible = table  # fallback: use all
        if not eligible:
            return {"action": "basic_attack", "weight": 1, "hp_bracket": "any",
                    "ability_effect": None, "ability_value": None, "ability_duration": None}

        total = sum(a["weight"] for a in eligible)
        roll = random.randint(1, total)
        cumulative = 0
        for action in eligible:
            cumulative += action["weight"]
            if roll <= cumulative:
                return action
        return eligible[-1]

    @staticmethod
    def resolve_turn(
        state: dict,
        player_action: dict,
        enemy: dict,
    ) -> "CombatResult":
        """
        Resolve one full combat turn.

        player_action: {type: "basic_attack"|"heavy_attack"|"cast_spell"|"defend"|"flee",
                        spell?: {...}}

        Returns a CombatResult dataclass.
        """
        ps = copy.deepcopy(state)   # player stats dict
        en = copy.deepcopy(enemy)   # enemy dict (has hp, attack, defense, speed, etc.)

        player_effects: list[dict] = ps.get("active_status_effects", [])
        enemy_effects: list[dict] = en.get("active_status_effects", [])

        player_hp = ps.get("hp", 100)
        player_mana = ps.get("mana", 50)
        player_attack = ps.get("attack", 10)
        player_defense = ps.get("defense", 5)
        player_speed = ps.get("speed", 10)
        arcane_affinity = ps.get("arcane_affinity", 5)
        strength = ps.get("strength", 10)

        enemy_hp = en.get("hp", 50)
        enemy_attack = en.get("attack", 10)
        enemy_defense = en.get("defense", 3)
        enemy_speed = en.get("speed", 8)
        enemy_max_hp = en.get("max_hp", en.get("hp", 50))

        # Apply stat-mod effects to player
        if has_effect(player_effects, "weaken"):
            player_attack = max(1, player_attack - get_effect_value(player_effects, "weaken") // 5)
        if has_effect(player_effects, "shatter"):
            player_defense = max(0, player_defense - get_effect_value(player_effects, "shatter") // 5)
        if has_effect(player_effects, "empower"):
            player_attack += get_effect_value(player_effects, "empower") // 5
        if has_effect(player_effects, "fortify"):
            player_defense += get_effect_value(player_effects, "fortify") // 5
        if has_effect(player_effects, "haste"):
            player_speed += get_effect_value(player_effects, "haste") // 5

        # Apply stat-mod effects to enemy
        if has_effect(enemy_effects, "weaken"):
            enemy_attack = max(1, enemy_attack - get_effect_value(enemy_effects, "weaken") // 5)
        if has_effect(enemy_effects, "shatter"):
            enemy_defense = max(0, enemy_defense - get_effect_value(enemy_effects, "shatter") // 5)

        # Speed check → turn order, extra action
        player_goes_first = player_speed >= enemy_speed
        player_extra_action = player_speed >= enemy_speed * EXTRA_ACTION_SPEED_RATIO
        enemy_extra_action = enemy_speed >= player_speed * EXTRA_ACTION_SPEED_RATIO

        player_damage_dealt = 0
        enemy_damage_dealt = 0
        player_action_label = ""
        enemy_action_label = ""

        action_type = player_action.get("type", "basic_attack")
        player_defending = action_type == "defend"
        player_stunned = has_effect(player_effects, "stun") or has_effect(player_effects, "fear")
        player_silenced = has_effect(player_effects, "silence")

        # ── Resolve player action ──────────────────────────────────────────
        if player_stunned:
            player_action_label = "⚡ Stunned — skips turn"
        elif action_type == "flee":
            player_action_label = "💨 Fled from battle"
            # Flee is handled at route level; here just mark it
        elif action_type == "defend":
            player_action_label = "🛡️ Defending"
        elif action_type == "cast_spell" and not player_silenced:
            spell = player_action.get("spell", {})
            mana_cost = spell.get("mana_cost", 10)
            if player_mana >= mana_cost:
                player_mana -= mana_cost
                dmg = GameEngine.calculate_damage(
                    player_attack, enemy_defense,
                    spell_stats=spell,
                    arcane_affinity=arcane_affinity,
                )
                # Apply spell effects to enemy
                for eff in spell.get("effects", []):
                    if eff.get("target", "enemy") == "enemy":
                        enemy_effects = apply_effect_to_target(
                            enemy_effects, eff["type"],
                            eff.get("value", 0), eff.get("duration", 2)
                        )
                player_damage_dealt = dmg
                player_action_label = f"✨ Cast {spell.get('name', 'Spell')} for {dmg} damage"
            else:
                # Not enough mana — fall back to basic attack
                dmg = GameEngine.calculate_damage(player_attack, enemy_defense)
                player_damage_dealt = dmg
                player_action_label = f"⚔️ Basic Attack (no mana) for {dmg} damage"
        elif action_type == "cast_spell" and player_silenced:
            player_action_label = "🔇 Silenced — cannot cast spells"
            dmg = GameEngine.calculate_damage(player_attack, enemy_defense)
            player_damage_dealt = dmg
            player_action_label += f" | ⚔️ Basic Attack for {dmg} damage"
        elif action_type == "heavy_attack":
            dmg = GameEngine.calculate_damage(player_attack, enemy_defense, is_heavy=True)
            player_damage_dealt = dmg
            player_action_label = f"⚔️ Heavy Attack for {dmg} damage"
        else:  # basic_attack
            dmg = GameEngine.calculate_damage(player_attack, enemy_defense)
            player_damage_dealt = dmg
            player_action_label = f"⚔️ Basic Attack for {dmg} damage"

        # Apply player damage to enemy
        enemy_hp = max(0, enemy_hp - player_damage_dealt)

        # ── Resolve enemy action ───────────────────────────────────────────
        enemy_stunned = has_effect(enemy_effects, "stun") or has_effect(enemy_effects, "fear")
        if enemy_stunned:
            enemy_action_label = "⚡ Enemy stunned — skips turn"
        else:
            enemy_hp_pct = enemy_hp / max(1, enemy_max_hp)
            chosen = GameEngine.pick_enemy_action(en, enemy_hp_pct)
            ea_type = chosen.get("action", "basic_attack")

            if ea_type == "defend":
                enemy_action_label = "🛡️ Enemy defends"
                # Enemy defending: reduce next player hit (tracked via effect)
                enemy_effects = apply_effect_to_target(enemy_effects, "fortify", 10, 1)
            elif ea_type == "heavy_attack":
                raw_dmg = GameEngine.calculate_damage(enemy_attack, player_defense, is_heavy=True)
                if player_defending:
                    raw_dmg = max(1, int(raw_dmg * DEFEND_DAMAGE_REDUCTION))
                # Reflect check
                if has_effect(player_effects, "reflect"):
                    enemy_hp = max(0, enemy_hp - raw_dmg)
                    enemy_action_label = f"🪞 Enemy heavy attack reflected for {raw_dmg} damage"
                else:
                    enemy_damage_dealt = raw_dmg
                    enemy_action_label = f"💥 Enemy Heavy Attack for {raw_dmg} damage"
            elif ea_type == "ability":
                eff_name = chosen.get("ability_effect")
                eff_val = chosen.get("ability_value", 0) or 0
                eff_dur = chosen.get("ability_duration", 2) or 2
                if eff_name:
                    player_effects = apply_effect_to_target(
                        player_effects, eff_name, eff_val, eff_dur
                    )
                    meta = EFFECT_META.get(eff_name, {"emoji": "✨"})
                    enemy_action_label = f"{meta['emoji']} Enemy uses {eff_name.replace('_', ' ').title()}"
                    # Ability may also deal direct damage
                    if eff_val and eff_name not in ("stun", "slow", "silence", "root",
                                                     "confuse", "fear", "weaken", "shatter",
                                                     "drain_mana", "empower", "fortify", "haste"):
                        pass  # DoT effects deal damage via tick, not immediately
                else:
                    enemy_action_label = "Enemy uses an ability"
            else:  # basic_attack
                raw_dmg = GameEngine.calculate_damage(enemy_attack, player_defense)
                if player_defending:
                    raw_dmg = max(1, int(raw_dmg * DEFEND_DAMAGE_REDUCTION))
                if has_effect(player_effects, "reflect"):
                    enemy_hp = max(0, enemy_hp - raw_dmg)
                    enemy_action_label = f"🪞 Enemy attack reflected for {raw_dmg} damage"
                else:
                    enemy_damage_dealt = raw_dmg
                    enemy_action_label = f"⚔️ Enemy Basic Attack for {raw_dmg} damage"

        # Apply enemy damage to player
        player_hp = max(0, player_hp - enemy_damage_dealt)

        # ── Tick status effects ────────────────────────────────────────────
        player_stats_tmp = {"hp": player_hp, "mana": player_mana,
                            "max_hp": ps.get("max_hp", 100), "max_mana": ps.get("max_mana", 50)}
        player_effects, p_dot, _ = tick_effects(player_effects, player_stats_tmp)
        player_hp = max(0, player_stats_tmp["hp"] - p_dot)
        player_mana = player_stats_tmp["mana"]

        enemy_stats_tmp = {"hp": enemy_hp, "max_hp": enemy_max_hp}
        enemy_effects, e_dot, _ = tick_effects(enemy_effects, enemy_stats_tmp)
        enemy_hp = max(0, enemy_stats_tmp["hp"] - e_dot)

        # ── Mana regen ────────────────────────────────────────────────────
        player_mana = min(ps.get("max_mana", 50), player_mana + BASE_MANA_REGEN)

        # ── Win/loss check ────────────────────────────────────────────────
        player_won = enemy_hp <= 0
        player_died = player_hp <= 0

        xp_gained = 0
        gold_gained = 0
        if player_won:
            xp_gained = en.get("xp", 0)
            gold_gained = random.randint(
                en.get("gold_min", 0), max(en.get("gold_min", 0), en.get("gold_max", 0))
            )

        return CombatResult(
            player_hp=player_hp,
            player_mana=player_mana,
            player_status_effects=player_effects,
            enemy_hp=enemy_hp,
            enemy_status_effects=enemy_effects,
            player_damage_dealt=player_damage_dealt,
            enemy_damage_dealt=enemy_damage_dealt,
            player_action_label=player_action_label,
            enemy_action_label=enemy_action_label,
            player_extra_action=player_extra_action,
            enemy_extra_action=enemy_extra_action,
            player_won=player_won,
            player_died=player_died,
            xp_gained=xp_gained,
            gold_gained=gold_gained,
            narration_context={
                "player_action": player_action_label,
                "enemy_action": enemy_action_label,
                "player_hp": player_hp,
                "enemy_hp": enemy_hp,
                "player_won": player_won,
                "player_died": player_died,
            },
        )

    # ── Exploration (delegated to exploration module) ───────────────────────────

    @staticmethod
    def _danger_tier(danger_meter: int) -> int:
        return ExplorationEngine._danger_tier(danger_meter)

    @staticmethod
    def explore_action(state: dict) -> tuple[dict, str]:
        return ExplorationEngine.explore_action(state)

    @staticmethod
    def _roll_event(floor: int, danger_tier: int) -> str:
        return ExplorationEngine._roll_event(floor, danger_tier)

    @staticmethod
    def roll_loot(floor: int, danger_tier: int, count: int = 2) -> list[dict]:
        return ExplorationEngine.roll_loot(floor, danger_tier, count)

    @staticmethod
    def roll_enemy(floor: int) -> dict:
        return ExplorationEngine.roll_enemy(floor)

    # ── Progression (delegated to progression module) ──────────────────────────

    @staticmethod
    def check_level_up(state: dict) -> tuple[dict, bool]:
        from app.services.game_engine.progression import ProgressionEngine
        return ProgressionEngine.check_level_up(state)

    @staticmethod
    def generate_shop_inventory(floor: int) -> list[dict]:
        from app.services.game_engine.progression import ProgressionEngine
        return ProgressionEngine.generate_shop_inventory(floor)

    # ── Shrine (delegated to shrine module) ────────────────────────────────────

    @staticmethod
    def roll_shrine_outcomes() -> list[dict]:
        from app.services.game_engine.shrine import ShrineEngine
        return ShrineEngine.roll_shrine_outcomes()

    @staticmethod
    def apply_shrine_outcome(state: dict, outcome: dict) -> dict:
        from app.services.game_engine.shrine import ShrineEngine
        return ShrineEngine.apply_shrine_outcome(state, outcome)