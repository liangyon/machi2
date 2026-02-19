"""
Run service — business logic for run routes.

Extracted from runs.py to keep routes thin.
"""

import json
import random
from typing import Optional

from fastapi import HTTPException

from app.models.run import GameState
from app.data.ingredients import CLASS_STARTING_INGREDIENTS, INGREDIENT_BY_ID
from app.data.enemies import MINI_BOSSES, FINAL_BOSS


# ─── Helpers ──────────────────────────────────────────────────────────────────


async def get_owned_run(run_id: str, player_id: str, db):
    """
    Fetch a run by ID and verify it belongs to the requesting player.
    Raises 404 if not found, 403 if owned by someone else.
    """
    row = await db.execute("SELECT * FROM runs WHERE id = ?", (run_id,))
    run = await row.fetchone()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    if run["player_id"] != player_id:
        raise HTTPException(status_code=403, detail="Not your run")
    return run


def load_state(run) -> dict:
    """Parse state_json from a DB row into a plain dict."""
    raw = run["state_json"] if isinstance(run["state_json"], str) else "{}"
    return json.loads(raw)


async def save_state(run_id: str, state: dict, db, status: str | None = None):
    """Persist updated state_json (and optionally status) to DB."""
    if status:
        await db.execute(
            "UPDATE runs SET state_json = ?, status = ?, floor = ? WHERE id = ?",
            (json.dumps(state), status, state.get("floor", 1), run_id),
        )
    else:
        await db.execute(
            "UPDATE runs SET state_json = ?, floor = ? WHERE id = ?",
            (json.dumps(state), state.get("floor", 1), run_id),
        )
    await db.commit()


# ─── Run creation ─────────────────────────────────────────────────────────────


def create_initial_state(player_class: str) -> GameState:
    """Create initial game state for a new run based on player class."""
    player_class = player_class.lower()
    if player_class == "mage":
        state = GameState(
            attack=7, defense=3, speed=9, arcane_affinity=15, strength=5,
            mana=80, max_mana=80,
        )
    else:  # knight / warrior default
        state = GameState(
            attack=12, defense=8, speed=8, arcane_affinity=3, strength=15,
            mana=30, max_mana=30,
        )

    # Starting ingredients by class
    starting_ids = CLASS_STARTING_INGREDIENTS.get(player_class, [])
    ingredient_inventory = []
    for ing_id in starting_ids:
        ing = INGREDIENT_BY_ID.get(ing_id)
        if ing:
            ingredient_inventory.append({
                "id": ing_id,
                "name": ing["name"],
                "tier": ing["tier"],
                "quantity": 1,
                "type": "ingredient",
            })
    state.ingredient_inventory = ingredient_inventory

    return state


# ─── Boss handling ────────────────────────────────────────────────────────────


def get_boss_for_floor(floor: int) -> dict:
    """Get boss definition for the given floor."""
    if floor == 8:
        boss_def = dict(FINAL_BOSS)
    else:
        boss_def = dict(MINI_BOSSES.get(floor, MINI_BOSSES[1]))

    boss_def["max_hp"] = boss_def["hp"]
    boss_def["active_status_effects"] = []
    return boss_def


# ─── Narration helpers ────────────────────────────────────────────────────────


def placeholder_room(floor: int, event_type: str) -> str:
    """Return a static placeholder room description. Phase 2 will use LLM."""
    descriptions = {
        "empty":  f"A quiet chamber on floor {floor}. Dust motes drift in the stale air.",
        "enemy":  f"You hear movement in the shadows of floor {floor}. Something stirs.",
        "chest":  f"A weathered chest sits in the corner, its lock long since rusted away.",
        "shrine": f"An ancient shrine pulses with ambiguous energy. Three offerings await.",
        "shop":   f"A hooded merchant materializes from the gloom. 'Wares for the brave...'",
        "boss":   f"The air grows heavy. A powerful presence fills the chamber.",
    }
    return descriptions.get(event_type, f"A dark corridor on floor {floor}.")


def shrine_flavor(outcome_type: str) -> str:
    """Return ambiguous shrine flavor text that doesn't reveal the outcome type."""
    flavors = {
        "buff":    [
            "A warm golden glow pulses gently from the altar.",
            "The runes shimmer with an inviting light.",
            "A gentle warmth radiates from the offering bowl.",
        ],
        "curse":   [
            "Shadows writhe at the altar's edge.",
            "The air grows cold near this offering.",
            "Something about this shrine feels wrong.",
        ],
        "neutral": [
            "The air smells faintly of ozone.",
            "The shrine hums with balanced energy.",
            "Neither light nor dark — something in between.",
        ],
    }
    options = flavors.get(outcome_type, ["The shrine awaits your choice."])
    return random.choice(options)


def build_narration(result) -> str:
    """Build placeholder combat narration. Phase 2 will use LLM."""
    lines = []
    if result.player_action_label:
        lines.append(result.player_action_label + ".")
    if result.enemy_action_label:
        lines.append(result.enemy_action_label + ".")
    if result.player_won:
        lines.append("The enemy falls. Victory!")
    elif result.player_died:
        lines.append("You have been defeated...")
    return " ".join(lines) if lines else "The battle continues."