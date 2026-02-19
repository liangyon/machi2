"""
Run routes — thin handlers that delegate to services.
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import StreamingResponse
import json
import uuid
from typing import Optional

from app.core.security import CurrentPlayer
from app.db.database import get_db
from app.models.schemas import StartRunRequest
from app.models.run import GameState
from app.services.game_engine import GameEngine
from app.services.run_service import (
    get_owned_run,
    load_state,
    save_state,
    create_initial_state,
    get_boss_for_floor,
    placeholder_room,
    shrine_flavor,
    build_narration,
)
from app.data.enemies import MINI_BOSSES, FINAL_BOSS

router = APIRouter()


# ─── Routes ───────────────────────────────────────────────────────────────────


@router.post("/start")
async def start_run(
    body: StartRunRequest,
    player: CurrentPlayer,
    db=Depends(get_db),
):
    """Create a new run for the authenticated player."""
    run_id = str(uuid.uuid4())
    player_class = body.player_class.lower()

    state = create_initial_state(player_class)
    state_dict = state.model_dump()

    await db.execute(
        """INSERT INTO runs (id, player_id, class, state_json, floor, status)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (run_id, player.oauth_id, player_class, json.dumps(state_dict), 1, "active"),
    )
    await db.commit()
    return {"run_id": run_id, "state": state_dict}


@router.get("/{run_id}/state")
async def get_run_state(
    run_id: str,
    player: CurrentPlayer,
    db=Depends(get_db),
):
    """Return full game state for a run. Player must own the run."""
    run = await get_owned_run(run_id, player.oauth_id, db)
    state = load_state(run)
    return {
        "id": run["id"],
        "player_class": run["class"],
        "state": state,
        "floor": run["floor"],
        "status": run["status"],
    }


@router.post("/{run_id}/explore")
async def explore(
    run_id: str,
    player: CurrentPlayer,
    db=Depends(get_db),
):
    """Take an exploration action. Returns room description + event type."""
    run = await get_owned_run(run_id, player.oauth_id, db)

    if run["status"] != "active":
        raise HTTPException(status_code=400, detail="Run is not active")

    state = load_state(run)
    floor = state.get("floor", 1)

    # Run the exploration engine
    updated_state, event_type = GameEngine.explore_action(state)
    danger_tier = GameEngine._danger_tier(updated_state["danger_meter"])

    response: dict = {
        "room": placeholder_room(floor, event_type),
        "event_type": event_type,
        "danger_meter": updated_state["danger_meter"],
        "action_count": updated_state["action_count"],
    }

    if event_type == "enemy":
        enemy = GameEngine.roll_enemy(floor)
        updated_state["current_enemy"] = enemy
        response["enemy"] = {
            "name": enemy["name"],
            "hp": enemy["hp"],
            "max_hp": enemy["max_hp"],
            "speed": enemy["speed"],
            "active_status_effects": [],
        }

    elif event_type == "chest":
        loot = GameEngine.roll_loot(floor, danger_tier)
        # Add to ingredient_inventory (cap at 20 slots)
        inv = updated_state.get("ingredient_inventory", [])
        for item in loot:
            existing = next((i for i in inv if i["id"] == item["id"]), None)
            if existing:
                existing["quantity"] += item["quantity"]
            elif len(inv) < 20:
                inv.append(item)
        updated_state["ingredient_inventory"] = inv
        response["loot"] = loot

    elif event_type == "shrine":
        outcomes = GameEngine.roll_shrine_outcomes()
        updated_state["rolled_shrine_outcomes"] = outcomes
        # Return ambiguous flavor only (not the actual effect)
        response["shrine_choices"] = [
            {"id": i, "flavor": shrine_flavor(o["type"])}
            for i, o in enumerate(outcomes)
        ]

    elif event_type == "shop":
        shop_items = GameEngine.generate_shop_inventory(floor)
        updated_state["shop_inventory"] = shop_items
        response["shop_items"] = shop_items

    await save_state(run_id, updated_state, db)
    return response


@router.post("/{run_id}/shrine/choose")
async def shrine_choose(
    run_id: str,
    player: CurrentPlayer,
    db=Depends(get_db),
    choice_id: int = Body(..., embed=True),
):
    """Apply chosen shrine outcome."""
    run = await get_owned_run(run_id, player.oauth_id, db)

    if run["status"] != "active":
        raise HTTPException(status_code=400, detail="Run is not active")

    state = load_state(run)
    outcomes = state.get("rolled_shrine_outcomes", [])

    if not outcomes or choice_id >= len(outcomes):
        raise HTTPException(status_code=400, detail="Invalid shrine choice")

    chosen = outcomes[choice_id]
    updated_state = GameEngine.apply_shrine_outcome(state, chosen)
    updated_state["rolled_shrine_outcomes"] = []  # clear after use

    await save_state(run_id, updated_state, db)
    return {
        "outcome": chosen["type"],
        "effect": chosen["effect"],
        "description": chosen["description"],
        "state": updated_state,
    }


@router.post("/{run_id}/combat/action")
async def combat_action(
    run_id: str,
    action: dict,
    player: CurrentPlayer,
    db=Depends(get_db),
):
    """Submit a combat action. Resolves turn, persists state, streams placeholder narration."""
    run = await get_owned_run(run_id, player.oauth_id, db)

    if run["status"] != "active":
        raise HTTPException(status_code=400, detail="Run is not active")

    state = load_state(run)
    enemy = state.get("current_enemy")

    if not enemy:
        raise HTTPException(status_code=400, detail="No active enemy")

    # Handle flee
    if action.get("type") == "flee":
        state["current_enemy"] = None
        await save_state(run_id, state, db)

        async def flee_stream():
            yield f"data: {json.dumps({'token': '💨 You fled from battle!'})}\n\n"
            yield f"data: {json.dumps({'result': {'fled': True, 'state': state}})}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(flee_stream(), media_type="text/event-stream")

    # Resolve combat turn
    result = GameEngine.resolve_turn(state, action, enemy)

    # Update player state
    state["hp"] = result.player_hp
    state["mana"] = result.player_mana
    state["active_status_effects"] = result.player_status_effects

    # Update enemy in state
    enemy["hp"] = result.enemy_hp
    enemy["active_status_effects"] = result.enemy_status_effects
    state["current_enemy"] = enemy

    new_run_status = run["status"]
    leveled_up = False
    level_up_info = None

    if result.player_won:
        # Grant XP + gold
        state["xp"] = state.get("xp", 0) + result.xp_gained
        state["gold"] = state.get("gold", 0) + result.gold_gained
        state["kills"] = state.get("kills", 0) + 1

        # Check if this was a boss (mini-boss or final boss)
        enemy_name = enemy.get("name", "")
        is_mini_boss = any(
            mb["name"] == enemy_name for mb in MINI_BOSSES.values()
        )
        is_final_boss = enemy_name == FINAL_BOSS["name"]

        if is_final_boss:
            # Victory! Mark the run as won
            new_run_status = "victory"
        elif is_mini_boss:
            # Advance to next floor after mini-boss
            state["floor"] = state.get("floor", 1) + 1
            state["danger_meter"] = 0
            state["action_count"] = 0
            level_up_info = level_up_info or {}
            level_up_info["floor_advanced"] = True
            level_up_info["new_floor"] = state["floor"]

        state["current_enemy"] = None

        # Check level up
        state, leveled_up = GameEngine.check_level_up(state)
        if leveled_up:
            level_up_info = {
                "new_level": state["level"],
                "unspent_stat_points": state["unspent_stat_points"],
                **(level_up_info or {}),
            }

    elif result.player_died:
        state["cause_of_death"] = f"Slain by {enemy.get('name', 'an enemy')}"
        new_run_status = "dead"

    await save_state(run_id, state, db, status=new_run_status)

    # Build result payload
    turn_result = {
        "player_hp": result.player_hp,
        "player_mana": result.player_mana,
        "player_status_effects": result.player_status_effects,
        "enemy_hp": result.enemy_hp,
        "enemy_status_effects": result.enemy_status_effects,
        "player_damage_dealt": result.player_damage_dealt,
        "enemy_damage_dealt": result.enemy_damage_dealt,
        "player_action_label": result.player_action_label,
        "enemy_action_label": result.enemy_action_label,
        "player_won": result.player_won,
        "player_died": result.player_died,
        "xp_gained": result.xp_gained,
        "gold_gained": result.gold_gained,
        "run_status": new_run_status,
        "leveled_up": leveled_up,
        "level_up_info": level_up_info,
        "state": state,
    }

    # Placeholder narration (Phase 2: real LLM)
    narration = build_narration(result)

    async def event_stream():
        # Stream narration tokens
        words = narration.split(" ")
        for word in words:
            yield f"data: {json.dumps({'token': word + ' '})}\n\n"
        # Send full result as final event
        yield f"data: {json.dumps({'result': turn_result})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/{run_id}/boss")
async def initiate_boss(
    run_id: str,
    player: CurrentPlayer,
    db=Depends(get_db),
):
    """Initiate mini-boss or final boss encounter."""
    run = await get_owned_run(run_id, player.oauth_id, db)

    if run["status"] != "active":
        raise HTTPException(status_code=400, detail="Run is not active")

    state = load_state(run)
    floor = state.get("floor", 1)

    boss_def = get_boss_for_floor(floor)
    state["current_enemy"] = boss_def

    await save_state(run_id, state, db)
    return {
        "boss": {
            "name": boss_def["name"],
            "hp": boss_def["hp"],
            "max_hp": boss_def["max_hp"],
            "speed": boss_def["speed"],
            "active_status_effects": [],
        },
        "is_final_boss": floor == 8,
    }


@router.post("/{run_id}/victory")
async def victory(
    run_id: str,
    player: CurrentPlayer,
    db=Depends(get_db),
    spell_to_bank: Optional[str] = None,
):
    """Handle run victory and optionally bank a spell to legacy spellbook."""
    run = await get_owned_run(run_id, player.oauth_id, db)
    state = load_state(run)

    await db.execute(
        "UPDATE runs SET status = 'victory', state_json = ? WHERE id = ?",
        (json.dumps(state), run_id),
    )

    # Bank spell to legacy spellbook (max 5)
    if spell_to_bank:
        row = await db.execute(
            "SELECT legacy_spellbook FROM players WHERE oauth_id = ?",
            (player.oauth_id,),
        )
        player_row = await row.fetchone()
        if player_row:
            spellbook = json.loads(player_row["legacy_spellbook"] or "[]")
            if len(spellbook) < 5 and spell_to_bank not in spellbook:
                spellbook.append(spell_to_bank)
                await db.execute(
                    "UPDATE players SET legacy_spellbook = ? WHERE oauth_id = ?",
                    (json.dumps(spellbook), player.oauth_id),
                )

    await db.commit()
    return {
        "message": "Victory!",
        "spell_banked": spell_to_bank,
        "state": state,
    }


@router.post("/{run_id}/allocate-stats")
async def allocate_stats(
    run_id: str,
    player: CurrentPlayer,
    db=Depends(get_db),
    body: dict = Body(...),
):
    """Spend unspent stat points from a level-up."""
    run = await get_owned_run(run_id, player.oauth_id, db)

    if run["status"] != "active":
        raise HTTPException(status_code=400, detail="Run is not active")

    state = load_state(run)
    stat = body.get("stat")
    points = int(body.get("points", 1))

    valid_stats = {"hp", "mana", "attack", "defense", "speed", "luck",
                   "arcane_affinity", "strength"}
    if stat not in valid_stats:
        raise HTTPException(status_code=400, detail=f"Invalid stat: {stat}")

    unspent = state.get("unspent_stat_points", 0)
    if points > unspent or points < 1:
        raise HTTPException(status_code=400, detail="Not enough unspent stat points")

    # Apply stat increase
    if stat == "hp":
        state["max_hp"] = state.get("max_hp", 100) + points * 5
        state["hp"] = min(state.get("hp", 100) + points * 5, state["max_hp"])
    elif stat == "mana":
        state["max_mana"] = state.get("max_mana", 50) + points * 5
        state["mana"] = min(state.get("mana", 50) + points * 5, state["max_mana"])
    else:
        state[stat] = state.get(stat, 5) + points * 2

    state["unspent_stat_points"] = unspent - points
    await save_state(run_id, state, db)

    return {"stat": stat, "points_spent": points, "state": state}


@router.post("/{run_id}/forge")
async def forge_spell(
    run_id: str,
    body: dict,
    player: CurrentPlayer,
    db=Depends(get_db),
):
    """Synthesize a spell via Grimoire check + LLM if new. (Phase 3)"""
    await get_owned_run(run_id, player.oauth_id, db)
    return {"spell": {"name": "Ember Bolt", "damage": 15, "mana_cost": 10}}