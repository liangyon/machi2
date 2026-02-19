"""
API request and response schemas for spell/grimoire endpoints.
"""

from pydantic import BaseModel
from typing import Optional


class ForgeRequest(BaseModel):
    ingredients: list[str]  # list of ingredient IDs


class GrimoireListResponse(BaseModel):
    spells: list[dict]  # list of GrimoireEntry as dict
    total: int
    page: int
    page_size: int