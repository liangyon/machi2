"""
Spell Synthesis LangGraph workflow.

Flow:
  [Check Grimoire DB]
    ├── (hit, no luck roll) → [Return cached spell]
    ├── (hit, luck roll succeeds) → [Check variant thresholds] → [Player chooses variant or new discovery]
    └── (miss / new variant) → [Call LLM in JSON mode]
                                  → [Pydantic validation]
                                       → (fail ×3) → [Return fallback spell]
                                       → (pass) → [Effect normalization]
                                                 → [Stat sanitization]
                                                 → [Content moderation filter]
                                                 → [Save to Grimoire DB]
                                                 → [Return spell]
"""
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END


class SpellSynthesisState(TypedDict):
    ingredient_key: str
    player_luck: int
    player_id: str
    cached_spell: Optional[dict]
    llm_attempts: int
    raw_llm_output: Optional[str]
    validated_spell: Optional[dict]
    final_spell: Optional[dict]
    error: Optional[str]


def check_grimoire(state: SpellSynthesisState) -> SpellSynthesisState:
    """Check if spell already exists in Grimoire DB."""
    # TODO: query DB for ingredient_key
    state["cached_spell"] = None
    return state


def return_cached(state: SpellSynthesisState) -> SpellSynthesisState:
    """Return the cached spell directly."""
    state["final_spell"] = state["cached_spell"]
    return state


def call_llm(state: SpellSynthesisState) -> SpellSynthesisState:
    """Call LLM in JSON mode to generate a new spell."""
    # TODO: call get_llm_client().complete(prompt, json_mode=True)
    state["llm_attempts"] = state.get("llm_attempts", 0) + 1
    state["raw_llm_output"] = None
    return state


def validate_spell(state: SpellSynthesisState) -> SpellSynthesisState:
    """Validate LLM output with Pydantic."""
    # TODO: parse and validate raw_llm_output
    state["validated_spell"] = None
    return state


def normalize_effects(state: SpellSynthesisState) -> SpellSynthesisState:
    """Normalize effect keywords."""
    return state


def sanitize_stats(state: SpellSynthesisState) -> SpellSynthesisState:
    """Apply damage formula constraints."""
    return state


def moderate_content(state: SpellSynthesisState) -> SpellSynthesisState:
    """Filter spell name + flavor text."""
    return state


def save_to_grimoire(state: SpellSynthesisState) -> SpellSynthesisState:
    """Persist validated spell to DB."""
    # TODO: insert into grimoire table
    state["final_spell"] = state["validated_spell"]
    return state


def return_fallback(state: SpellSynthesisState) -> SpellSynthesisState:
    """Return a safe fallback spell after 3 LLM failures."""
    state["final_spell"] = {
        "spell_name": "Arcane Bolt",
        "flavor_text": "A basic magical projectile.",
        "stats": {"damage": 10, "mana_cost": 5, "cooldown": 0, "damage_type": "arcane"},
        "effects": [],
    }
    return state


def route_after_grimoire_check(state: SpellSynthesisState) -> str:
    if state["cached_spell"]:
        return "return_cached"
    return "call_llm"


def route_after_validation(state: SpellSynthesisState) -> str:
    if state["validated_spell"]:
        return "normalize_effects"
    if state.get("llm_attempts", 0) >= 3:
        return "return_fallback"
    return "call_llm"


def build_spell_synthesis_graph():
    graph = StateGraph(SpellSynthesisState)

    graph.add_node("check_grimoire", check_grimoire)
    graph.add_node("return_cached", return_cached)
    graph.add_node("call_llm", call_llm)
    graph.add_node("validate_spell", validate_spell)
    graph.add_node("normalize_effects", normalize_effects)
    graph.add_node("sanitize_stats", sanitize_stats)
    graph.add_node("moderate_content", moderate_content)
    graph.add_node("save_to_grimoire", save_to_grimoire)
    graph.add_node("return_fallback", return_fallback)

    graph.set_entry_point("check_grimoire")
    graph.add_conditional_edges("check_grimoire", route_after_grimoire_check)
    graph.add_edge("return_cached", END)
    graph.add_edge("call_llm", "validate_spell")
    graph.add_conditional_edges("validate_spell", route_after_validation)
    graph.add_edge("normalize_effects", "sanitize_stats")
    graph.add_edge("sanitize_stats", "moderate_content")
    graph.add_edge("moderate_content", "save_to_grimoire")
    graph.add_edge("save_to_grimoire", END)
    graph.add_edge("return_fallback", END)

    return graph.compile()


spell_synthesis_graph = build_spell_synthesis_graph()
