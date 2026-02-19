"""
API request and response schemas for run endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal


class StartRunRequest(BaseModel):
    player_class: str
    starting_legacy_spells: list[str] = []


class RunStateResponse(BaseModel):
    id: str
    player_class: str
    state: dict  # GameState as dict
    floor: int
    status: str