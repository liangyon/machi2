"""
Room Generation LangGraph workflow.

Flow:
  [Determine event type (weighted random by floor)]
    → [Generate room description via LLM]
    → [Return room + event type]
"""
import random
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

EVENT_WEIGHTS = {
    "empty": 30,
    "enemy": 35,
    "chest": 15,
    "shrine": 10,
    "shop": 5,
    "boss": 5,
}


class RoomState(TypedDict):
    floor: int
    event_type: Optional[str]
    room_description: Optional[str]


def determine_event_type(state: RoomState) -> RoomState:
    """Weighted random event type selection based on floor."""
    population = list(EVENT_WEIGHTS.keys())
    weights = list(EVENT_WEIGHTS.values())
    state["event_type"] = random.choices(population, weights=weights, k=1)[0]
    return state


def generate_room_description(state: RoomState) -> RoomState:
    """Generate room description via LLM."""
    # TODO: call get_llm_client().complete(prompt)
    state["room_description"] = f"A mysterious room on floor {state['floor']}."
    return state


def build_room_generation_graph():
    graph = StateGraph(RoomState)

    graph.add_node("determine_event_type", determine_event_type)
    graph.add_node("generate_room_description", generate_room_description)

    graph.set_entry_point("determine_event_type")
    graph.add_edge("determine_event_type", "generate_room_description")
    graph.add_edge("generate_room_description", END)

    return graph.compile()


room_generation_graph = build_room_generation_graph()
