"""
Ingredient catalog and floor loot tables.

Tiers: basic, rare, legendary, conceptual
Each ingredient: id, name, tier, floors_available (list of floor numbers)

Loot tables per floor: weighted list of (ingredient_id, weight) tuples.
Higher danger tier shifts weights toward rarer ingredients.
"""

from typing import TypedDict


class IngredientDef(TypedDict):
    id: str
    name: str
    tier: str   # "basic" | "rare" | "legendary" | "conceptual"
    floors: list[int]


ALL_INGREDIENTS: list[IngredientDef] = [
    # ── Basic ──────────────────────────────────────────────────────────────
    {"id": "fire",      "name": "Fire",      "tier": "basic",     "floors": [1,2,3,4,5,6,7,8]},
    {"id": "ice",       "name": "Ice",       "tier": "basic",     "floors": [1,2,3,4,5,6,7,8]},
    {"id": "water",     "name": "Water",     "tier": "basic",     "floors": [1,2,3,4,5,6,7,8]},
    {"id": "earth",     "name": "Earth",     "tier": "basic",     "floors": [1,2,3,4,5,6,7,8]},
    {"id": "wind",      "name": "Wind",      "tier": "basic",     "floors": [1,2,3,4,5,6,7,8]},
    {"id": "stone",     "name": "Stone",     "tier": "basic",     "floors": [1,2,3,4,5,6,7,8]},
    {"id": "iron",      "name": "Iron",      "tier": "basic",     "floors": [1,2,3,4,5,6,7,8]},
    {"id": "blood",     "name": "Blood",     "tier": "basic",     "floors": [1,2,3,4,5,6,7,8]},
    {"id": "shadow",    "name": "Shadow",    "tier": "basic",     "floors": [1,2,3,4,5,6,7,8]},
    {"id": "lightning", "name": "Lightning", "tier": "basic",     "floors": [1,2,3,4,5,6,7,8]},

    # ── Rare ───────────────────────────────────────────────────────────────
    {"id": "light",     "name": "Light",     "tier": "rare",      "floors": [3,4,5,6,7,8]},
    {"id": "dark",      "name": "Dark",      "tier": "rare",      "floors": [3,4,5,6,7,8]},
    {"id": "storm",     "name": "Storm",     "tier": "rare",      "floors": [3,4,5,6,7,8]},
    {"id": "plague",    "name": "Plague",    "tier": "rare",      "floors": [3,4,5,6,7,8]},
    {"id": "mirror",    "name": "Mirror",    "tier": "rare",      "floors": [4,5,6,7,8]},
    {"id": "time",      "name": "Time",      "tier": "rare",      "floors": [4,5,6,7,8]},
    {"id": "frost",     "name": "Frost",     "tier": "rare",      "floors": [3,4,5,6,7,8]},
    {"id": "venom",     "name": "Venom",     "tier": "rare",      "floors": [3,4,5,6,7,8]},

    # ── Legendary ──────────────────────────────────────────────────────────
    {"id": "void",      "name": "Void",      "tier": "legendary", "floors": [6,7,8]},
    {"id": "abyss",     "name": "Abyss",     "tier": "legendary", "floors": [6,7,8]},
    {"id": "eternity",  "name": "Eternity",  "tier": "legendary", "floors": [6,7,8]},
    {"id": "ruin",      "name": "Ruin",      "tier": "legendary", "floors": [5,6,7,8]},
    {"id": "oblivion",  "name": "Oblivion",  "tier": "legendary", "floors": [6,7,8]},
    {"id": "chaos",     "name": "Chaos",     "tier": "legendary", "floors": [5,6,7,8]},

    # ── Conceptual ─────────────────────────────────────────────────────────
    {"id": "heroic",    "name": "Heroic",    "tier": "conceptual", "floors": [7,8]},
    {"id": "hunger",    "name": "Hunger",    "tier": "conceptual", "floors": [6,7,8]},
    {"id": "echo",      "name": "Echo",      "tier": "conceptual", "floors": [7,8]},
    {"id": "grief",     "name": "Grief",     "tier": "conceptual", "floors": [6,7,8]},
    {"id": "triumph",   "name": "Triumph",   "tier": "conceptual", "floors": [7,8]},
    {"id": "silence",   "name": "Silence",   "tier": "conceptual", "floors": [6,7,8]},
    {"id": "memory",    "name": "Memory",    "tier": "conceptual", "floors": [8]},
]

# Index by id for fast lookup
INGREDIENT_BY_ID: dict[str, IngredientDef] = {i["id"]: i for i in ALL_INGREDIENTS}

# ─── Loot tables ──────────────────────────────────────────────────────────────
# Each entry: (ingredient_id, weight)
# Weights are relative; higher = more likely.
# Danger tier shifts: at danger tier 2+ rare ingredients get a bonus weight multiplier.

_BASIC_IDS = [i["id"] for i in ALL_INGREDIENTS if i["tier"] == "basic"]
_RARE_IDS   = [i["id"] for i in ALL_INGREDIENTS if i["tier"] == "rare"]
_LEG_IDS    = [i["id"] for i in ALL_INGREDIENTS if i["tier"] == "legendary"]
_CON_IDS    = [i["id"] for i in ALL_INGREDIENTS if i["tier"] == "conceptual"]


def get_floor_loot_pool(floor: int, danger_tier: int) -> list[tuple[str, int]]:
    """
    Return a weighted pool of ingredient IDs for the given floor and danger tier.
    danger_tier: 1 (0-30%), 2 (31-60%), 3 (61-85%), 4 (86-100%)
    """
    pool: list[tuple[str, int]] = []

    # Basic ingredients available on all floors
    basic_weight = 60
    for ing_id in _BASIC_IDS:
        pool.append((ing_id, basic_weight))

    # Rare ingredients: available from floor 3+
    if floor >= 3:
        rare_weight = 25 + (danger_tier - 1) * 10  # 25 / 35 / 45 / 55
        for ing_id in _RARE_IDS:
            ing = INGREDIENT_BY_ID[ing_id]
            if floor in ing["floors"]:
                pool.append((ing_id, rare_weight))

    # Legendary: floor 5+
    if floor >= 5:
        leg_weight = 8 + (danger_tier - 1) * 8  # 8 / 16 / 24 / 32
        for ing_id in _LEG_IDS:
            ing = INGREDIENT_BY_ID[ing_id]
            if floor in ing["floors"]:
                pool.append((ing_id, leg_weight))

    # Conceptual: floor 6+, only at danger tier 3+
    if floor >= 6 and danger_tier >= 3:
        con_weight = 4 + (danger_tier - 3) * 4  # 4 / 8
        for ing_id in _CON_IDS:
            ing = INGREDIENT_BY_ID[ing_id]
            if floor in ing["floors"]:
                pool.append((ing_id, con_weight))

    return pool


# ─── Starting ingredients by class ────────────────────────────────────────────

STARTING_INGREDIENTS: dict[str, list[str]] = {
    "knight": ["iron", "shield_shard", "blood", "stone"],   # Basic tier
    "mage":   ["fire", "time", "void", "mirror"],            # Basic + Rare + Legendary
}

# Normalise: knight gets basic only, mage gets their special set
# (void and mirror may not be in floor 1 pool but are given as class starters)
CLASS_STARTING_INGREDIENTS: dict[str, list[str]] = {
    "knight": ["iron", "blood", "stone", "lightning"],
    "mage":   ["fire", "time", "mirror", "void"],
}

# ─── Shop item definitions ────────────────────────────────────────────────────

class ShopItem(TypedDict):
    id: str
    name: str
    type: str    # "ingredient" | "consumable" | "equipment"
    tier: str
    price: int
    ingredient_id: str | None   # for ingredient type
    effect: str | None          # for consumable type


CONSUMABLES = [
    {"id": "hp_potion_small",  "name": "HP Potion",       "type": "consumable", "tier": "basic",
     "effect": "heal_30",  "ingredient_id": None},
    {"id": "hp_potion_large",  "name": "Greater HP Potion","type": "consumable", "tier": "rare",
     "effect": "heal_60",  "ingredient_id": None},
    {"id": "mana_potion_small","name": "Mana Potion",      "type": "consumable", "tier": "basic",
     "effect": "mana_20",  "ingredient_id": None},
    {"id": "mana_potion_large","name": "Greater Mana Potion","type": "consumable","tier": "rare",
     "effect": "mana_40",  "ingredient_id": None},
]

EQUIPMENT_BY_FLOOR: dict[int, list[dict]] = {
    1: [
        {"id": "iron_sword",    "name": "Iron Sword",    "type": "equipment", "tier": "basic",
         "slot": "weapon", "stat_bonus": {"attack": 3},  "price": 60,  "ingredient_id": None, "effect": None},
        {"id": "leather_armor", "name": "Leather Armor", "type": "equipment", "tier": "basic",
         "slot": "armor",  "stat_bonus": {"defense": 3}, "price": 55,  "ingredient_id": None, "effect": None},
        {"id": "lucky_charm",   "name": "Lucky Charm",   "type": "equipment", "tier": "basic",
         "slot": "accessory", "stat_bonus": {"luck": 3}, "price": 50,  "ingredient_id": None, "effect": None},
    ],
    2: [
        {"id": "steel_sword",   "name": "Steel Sword",   "type": "equipment", "tier": "basic",
         "slot": "weapon", "stat_bonus": {"attack": 5},  "price": 90,  "ingredient_id": None, "effect": None},
        {"id": "chain_mail",    "name": "Chain Mail",    "type": "equipment", "tier": "basic",
         "slot": "armor",  "stat_bonus": {"defense": 5}, "price": 85,  "ingredient_id": None, "effect": None},
        {"id": "swift_boots",   "name": "Swift Boots",   "type": "equipment", "tier": "rare",
         "slot": "accessory", "stat_bonus": {"speed": 3},"price": 100, "ingredient_id": None, "effect": None},
    ],
    3: [
        {"id": "shadow_blade",  "name": "Shadow Blade",  "type": "equipment", "tier": "rare",
         "slot": "weapon", "stat_bonus": {"attack": 7},  "price": 130, "ingredient_id": None, "effect": None},
        {"id": "mage_robe",     "name": "Mage Robe",     "type": "equipment", "tier": "rare",
         "slot": "armor",  "stat_bonus": {"arcane_affinity": 5}, "price": 120, "ingredient_id": None, "effect": None},
        {"id": "arcane_focus",  "name": "Arcane Focus",  "type": "equipment", "tier": "rare",
         "slot": "accessory", "stat_bonus": {"mana": 15},"price": 110, "ingredient_id": None, "effect": None},
    ],
    4: [
        {"id": "venom_dagger",  "name": "Venom Dagger",  "type": "equipment", "tier": "rare",
         "slot": "weapon", "stat_bonus": {"attack": 9, "luck": 2}, "price": 160, "ingredient_id": None, "effect": None},
        {"id": "plate_armor",   "name": "Plate Armor",   "type": "equipment", "tier": "rare",
         "slot": "armor",  "stat_bonus": {"defense": 9}, "price": 150, "ingredient_id": None, "effect": None},
        {"id": "storm_ring",    "name": "Storm Ring",    "type": "equipment", "tier": "rare",
         "slot": "accessory", "stat_bonus": {"speed": 4, "attack": 3}, "price": 140, "ingredient_id": None, "effect": None},
    ],
    5: [
        {"id": "void_blade",    "name": "Void Blade",    "type": "equipment", "tier": "legendary",
         "slot": "weapon", "stat_bonus": {"attack": 13}, "price": 220, "ingredient_id": None, "effect": None},
        {"id": "abyss_armor",   "name": "Abyss Armor",   "type": "equipment", "tier": "legendary",
         "slot": "armor",  "stat_bonus": {"defense": 12},"price": 210, "ingredient_id": None, "effect": None},
        {"id": "chaos_pendant", "name": "Chaos Pendant", "type": "equipment", "tier": "legendary",
         "slot": "accessory", "stat_bonus": {"luck": 8}, "price": 200, "ingredient_id": None, "effect": None},
    ],
    6: [
        {"id": "ruin_sword",    "name": "Ruin Sword",    "type": "equipment", "tier": "legendary",
         "slot": "weapon", "stat_bonus": {"attack": 16}, "price": 270, "ingredient_id": None, "effect": None},
        {"id": "oblivion_robe", "name": "Oblivion Robe", "type": "equipment", "tier": "legendary",
         "slot": "armor",  "stat_bonus": {"arcane_affinity": 10, "defense": 8}, "price": 260, "ingredient_id": None, "effect": None},
        {"id": "eternity_ring", "name": "Eternity Ring", "type": "equipment", "tier": "legendary",
         "slot": "accessory", "stat_bonus": {"speed": 6, "luck": 5}, "price": 250, "ingredient_id": None, "effect": None},
    ],
    7: [
        {"id": "sovereign_blade","name": "Sovereign Blade","type": "equipment","tier": "legendary",
         "slot": "weapon", "stat_bonus": {"attack": 20}, "price": 330, "ingredient_id": None, "effect": None},
        {"id": "archon_plate",  "name": "Archon Plate",  "type": "equipment", "tier": "legendary",
         "slot": "armor",  "stat_bonus": {"defense": 18},"price": 320, "ingredient_id": None, "effect": None},
        {"id": "memory_shard",  "name": "Memory Shard",  "type": "equipment", "tier": "conceptual",
         "slot": "accessory", "stat_bonus": {"luck": 10, "arcane_affinity": 8}, "price": 350, "ingredient_id": None, "effect": None},
    ],
    8: [
        {"id": "sovereign_blade","name": "Sovereign Blade","type": "equipment","tier": "legendary",
         "slot": "weapon", "stat_bonus": {"attack": 20}, "price": 330, "ingredient_id": None, "effect": None},
        {"id": "archon_plate",  "name": "Archon Plate",  "type": "equipment", "tier": "legendary",
         "slot": "armor",  "stat_bonus": {"defense": 18},"price": 320, "ingredient_id": None, "effect": None},
        {"id": "memory_shard",  "name": "Memory Shard",  "type": "equipment", "tier": "conceptual",
         "slot": "accessory", "stat_bonus": {"luck": 10, "arcane_affinity": 8}, "price": 350, "ingredient_id": None, "effect": None},
    ],
}

# Base prices for ingredients in shops (scaled by floor)
INGREDIENT_BASE_PRICES: dict[str, int] = {
    "basic": 30,
    "rare": 80,
    "legendary": 200,
    "conceptual": 400,
}
