"""
Combat Narration LangGraph workflow.

Flow:
  [Speed check → determine turn order + extra actions]
    → [Pre-damage hooks (reflect, shield)]
    → [Resolve actions in order]
    → [Tick all status effects]
    → [Build narration prompt with full context]
    → [Stream LLM narration via SSE]
    → [Check phase transition] → (yes) → [Generate boss phase narration]
"""
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END


class CombatState(TypedDict):
    run_id: str
    player_action: dict
    player_stats: dict
    enemy_stats: dict
    turn_order: list
    pre_damage_hooks_applied: bool
    resolved_actions: list
    status_effects_ticked: bool
    narration_prompt: Optional[str]
    narration_tokens: list
    phase_transition: bool
    boss_phase_narration: Optional[str]


def speed_check(state: CombatState) -> CombatState:
    """Determine turn order based on Speed stat."""
    # TODO: compare player speed vs enemy speed, handle extra actions
    state["turn_order"] = ["player", "enemy"]
    return state


def apply_pre_damage_hooks(state: CombatState) -> CombatState:
    """Apply reflect, shield, and other pre-damage effects."""
    state["pre_damage_hooks_applied"] = True
    return state


def resolve_actions(state: CombatState) -> CombatState:
    """Resolve all actions in turn order."""
    state["resolved_actions"] = []
    return state


def tick_status_effects(state: CombatState) -> CombatState:
    """Decrement all active status effect counters."""
    state["status_effects_ticked"] = True
    return state


def build_narration_prompt(state: CombatState) -> CombatState:
    """Construct the LLM narration prompt from full combat context."""
    state["narration_prompt"] = "Narrate this combat turn..."
    return state


def stream_narration(state: CombatState) -> CombatState:
    """Stream LLM narration tokens via SSE."""
    # TODO: call get_llm_client().stream(state["narration_prompt"])
    state["narration_tokens"] = []
    return state


def check_phase_transition(state: CombatState) -> CombatState:
    """Check if boss phase transition should trigger."""
    state["phase_transition"] = False
    return state


def generate_boss_phase_narration(state: CombatState) -> CombatState:
    """Generate narration for boss phase change."""
    state["boss_phase_narration"] = "The boss enters a new phase!"
    return state


def route_phase_transition(state: CombatState) -> str:
    if state.get("phase_transition"):
        return "generate_boss_phase_narration"
    return END


def build_combat_narration_graph():
    graph = StateGraph(CombatState)

    graph.add_node("speed_check", speed_check)
    graph.add_node("apply_pre_damage_hooks", apply_pre_damage_hooks)
    graph.add_node("resolve_actions", resolve_actions)
    graph.add_node("tick_status_effects", tick_status_effects)
    graph.add_node("build_narration_prompt", build_narration_prompt)
    graph.add_node("stream_narration", stream_narration)
    graph.add_node("check_phase_transition", check_phase_transition)
    graph.add_node("generate_boss_phase_narration", generate_boss_phase_narration)

    graph.set_entry_point("speed_check")
    graph.add_edge("speed_check", "apply_pre_damage_hooks")
    graph.add_edge("apply_pre_damage_hooks", "resolve_actions")
    graph.add_edge("resolve_actions", "tick_status_effects")
    graph.add_edge("tick_status_effects", "build_narration_prompt")
    graph.add_edge("build_narration_prompt", "stream_narration")
    graph.add_edge("stream_narration", "check_phase_transition")
    graph.add_conditional_edges("check_phase_transition", route_phase_transition)
    graph.add_edge("generate_boss_phase_narration", END)

    return graph.compile()


combat_narration_graph = build_combat_narration_graph()
