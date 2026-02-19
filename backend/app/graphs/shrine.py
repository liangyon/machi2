"""
Shrine LangGraph workflow.

Flow:
  [Roll 3 outcomes server-side (buff / curse / neutral)]
    → [Generate 3 ambiguous flavor descriptions via LLM]
    → [Player picks one]
    → [Reveal and apply outcome]
"""
import random
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

OUTCOME_POOL = ["buff", "curse", "neutral"]


class ShrineState(TypedDict):
    run_id: str
    rolled_outcomes: list  # e.g. ["buff", "curse", "neutral"]
    flavor_descriptions: list  # 3 ambiguous strings
    player_choice: Optional[int]  # index 0-2
    revealed_outcome: Optional[str]
    applied: bool


def roll_outcomes(state: ShrineState) -> ShrineState:
    """Roll 3 outcomes server-side."""
    state["rolled_outcomes"] = random.choices(OUTCOME_POOL, k=3)
    return state


def generate_flavor_descriptions(state: ShrineState) -> ShrineState:
    """Generate 3 ambiguous flavor descriptions via LLM."""
    # TODO: call LLM for each outcome (without revealing which is which)
    state["flavor_descriptions"] = [
        "A warm golden glow pulses gently.",
        "Shadows writhe at the altar's edge.",
        "The air smells faintly of ozone.",
    ]
    return state


def reveal_and_apply(state: ShrineState) -> ShrineState:
    """Reveal the chosen outcome and apply it to game state."""
    choice = state.get("player_choice", 0)
    state["revealed_outcome"] = state["rolled_outcomes"][choice]
    state["applied"] = True
    return state


def build_shrine_graph():
    graph = StateGraph(ShrineState)

    graph.add_node("roll_outcomes", roll_outcomes)
    graph.add_node("generate_flavor_descriptions", generate_flavor_descriptions)
    graph.add_node("reveal_and_apply", reveal_and_apply)

    graph.set_entry_point("roll_outcomes")
    graph.add_edge("roll_outcomes", "generate_flavor_descriptions")
    graph.add_edge("generate_flavor_descriptions", END)  # pause for player choice
    # reveal_and_apply is invoked separately after player picks

    return graph.compile()


shrine_graph = build_shrine_graph()
