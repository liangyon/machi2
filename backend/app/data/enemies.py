"""
Enemy definitions for all 8 floors.

Each enemy entry:
  name, hp, speed, attack, defense, xp, gold_min, gold_max
  action_table: list of {action, weight, hp_bracket ("high"=above 50%, "low"=below, "any")}
    action types: "basic_attack", "heavy_attack", "ability", "defend"
    ability_effect: optional effect primitive name applied on ability use

Mini-bosses appear at the end of floors 1–7.
Final boss is floor 8.
"""

from typing import TypedDict, Optional


class EnemyAction(TypedDict):
    action: str           # "basic_attack" | "heavy_attack" | "ability" | "defend"
    weight: int
    hp_bracket: str       # "high" | "low" | "any"
    ability_effect: Optional[str]   # effect primitive name, e.g. "burn", "stun"
    ability_value: Optional[int]    # damage or effect magnitude
    ability_duration: Optional[int] # turns for status effects


class EnemyDef(TypedDict):
    name: str
    hp: int
    speed: int
    attack: int
    defense: int
    xp: int
    gold_min: int
    gold_max: int
    action_table: list[EnemyAction]


def _action(action: str, weight: int, hp_bracket: str = "any",
            ability_effect: str | None = None,
            ability_value: int | None = None,
            ability_duration: int | None = None) -> EnemyAction:
    return {
        "action": action,
        "weight": weight,
        "hp_bracket": hp_bracket,
        "ability_effect": ability_effect,
        "ability_value": ability_value,
        "ability_duration": ability_duration,
    }


# ─── Floor 1 ──────────────────────────────────────────────────────────────────

FLOOR_1_ENEMIES: list[EnemyDef] = [
    {
        "name": "Goblin Scout",
        "hp": 28, "speed": 9, "attack": 7, "defense": 1,
        "xp": 18, "gold_min": 5, "gold_max": 12,
        "action_table": [
            _action("basic_attack", 70),
            _action("heavy_attack", 20, "low"),
            _action("defend", 10, "low"),
        ],
    },
    {
        "name": "Skeleton",
        "hp": 35, "speed": 7, "attack": 9, "defense": 3,
        "xp": 22, "gold_min": 6, "gold_max": 14,
        "action_table": [
            _action("basic_attack", 60),
            _action("heavy_attack", 30),
            _action("defend", 10, "low"),
        ],
    },
    {
        "name": "Giant Rat",
        "hp": 22, "speed": 12, "attack": 6, "defense": 0,
        "xp": 15, "gold_min": 3, "gold_max": 8,
        "action_table": [
            _action("basic_attack", 60),
            _action("ability", 40, ability_effect="bleed", ability_value=3, ability_duration=2),
        ],
    },
]

FLOOR_1_MINI_BOSS: EnemyDef = {
    "name": "Goblin Warchief",
    "hp": 90, "speed": 10, "attack": 13, "defense": 4,
    "xp": 160, "gold_min": 40, "gold_max": 60,
    "action_table": [
        _action("basic_attack", 50, "high"),
        _action("heavy_attack", 30, "high"),
        _action("ability", 20, "high", ability_effect="weaken", ability_value=20, ability_duration=2),
        _action("basic_attack", 20, "low"),
        _action("heavy_attack", 50, "low"),
        _action("ability", 30, "low", ability_effect="stun", ability_value=0, ability_duration=1),
    ],
}

# ─── Floor 2 ──────────────────────────────────────────────────────────────────

FLOOR_2_ENEMIES: list[EnemyDef] = [
    {
        "name": "Dark Slime",
        "hp": 45, "speed": 5, "attack": 10, "defense": 2,
        "xp": 28, "gold_min": 8, "gold_max": 16,
        "action_table": [
            _action("basic_attack", 50),
            _action("ability", 50, ability_effect="poison", ability_value=4, ability_duration=3),
        ],
    },
    {
        "name": "Cursed Soldier",
        "hp": 55, "speed": 8, "attack": 12, "defense": 5,
        "xp": 32, "gold_min": 10, "gold_max": 20,
        "action_table": [
            _action("basic_attack", 60),
            _action("heavy_attack", 25, "low"),
            _action("defend", 15, "high"),
        ],
    },
    {
        "name": "Shadow Bat",
        "hp": 30, "speed": 14, "attack": 8, "defense": 1,
        "xp": 20, "gold_min": 5, "gold_max": 12,
        "action_table": [
            _action("basic_attack", 70),
            _action("ability", 30, ability_effect="drain_mana", ability_value=8, ability_duration=2),
        ],
    },
]

FLOOR_2_MINI_BOSS: EnemyDef = {
    "name": "Stone Golem",
    "hp": 130, "speed": 6, "attack": 16, "defense": 8,
    "xp": 220, "gold_min": 55, "gold_max": 80,
    "action_table": [
        _action("basic_attack", 40, "high"),
        _action("heavy_attack", 40, "high"),
        _action("defend", 20, "high"),
        _action("heavy_attack", 60, "low"),
        _action("ability", 40, "low", ability_effect="shatter", ability_value=30, ability_duration=2),
    ],
}

# ─── Floor 3 ──────────────────────────────────────────────────────────────────

FLOOR_3_ENEMIES: list[EnemyDef] = [
    {
        "name": "Plague Rat",
        "hp": 50, "speed": 11, "attack": 11, "defense": 2,
        "xp": 38, "gold_min": 12, "gold_max": 22,
        "action_table": [
            _action("basic_attack", 40),
            _action("ability", 60, ability_effect="poison", ability_value=5, ability_duration=3),
        ],
    },
    {
        "name": "Bone Archer",
        "hp": 48, "speed": 10, "attack": 14, "defense": 2,
        "xp": 40, "gold_min": 14, "gold_max": 24,
        "action_table": [
            _action("basic_attack", 60),
            _action("heavy_attack", 30, "low"),
            _action("ability", 10, ability_effect="slow", ability_value=0, ability_duration=2),
        ],
    },
    {
        "name": "Frost Wisp",
        "hp": 38, "speed": 13, "attack": 10, "defense": 1,
        "xp": 30, "gold_min": 10, "gold_max": 18,
        "action_table": [
            _action("basic_attack", 50),
            _action("ability", 50, ability_effect="frostbite", ability_value=5, ability_duration=2),
        ],
    },
]

FLOOR_3_MINI_BOSS: EnemyDef = {
    "name": "Plague Witch",
    "hp": 160, "speed": 9, "attack": 18, "defense": 6,
    "xp": 280, "gold_min": 70, "gold_max": 100,
    "action_table": [
        _action("basic_attack", 30, "high"),
        _action("ability", 50, "high", ability_effect="poison", ability_value=8, ability_duration=3),
        _action("heavy_attack", 20, "high"),
        _action("heavy_attack", 40, "low"),
        _action("ability", 40, "low", ability_effect="weaken", ability_value=25, ability_duration=3),
        _action("ability", 20, "low", ability_effect="silence", ability_value=0, ability_duration=2),
    ],
}

# ─── Floor 4 ──────────────────────────────────────────────────────────────────

FLOOR_4_ENEMIES: list[EnemyDef] = [
    {
        "name": "Venom Serpent",
        "hp": 65, "speed": 12, "attack": 15, "defense": 3,
        "xp": 50, "gold_min": 16, "gold_max": 28,
        "action_table": [
            _action("basic_attack", 40),
            _action("ability", 60, ability_effect="poison", ability_value=7, ability_duration=3),
        ],
    },
    {
        "name": "Dark Knight",
        "hp": 80, "speed": 9, "attack": 18, "defense": 10,
        "xp": 58, "gold_min": 20, "gold_max": 35,
        "action_table": [
            _action("basic_attack", 50, "high"),
            _action("defend", 30, "high"),
            _action("heavy_attack", 20, "high"),
            _action("heavy_attack", 60, "low"),
            _action("ability", 40, "low", ability_effect="weaken", ability_value=20, ability_duration=2),
        ],
    },
    {
        "name": "Storm Elemental",
        "hp": 58, "speed": 15, "attack": 16, "defense": 4,
        "xp": 52, "gold_min": 18, "gold_max": 30,
        "action_table": [
            _action("basic_attack", 50),
            _action("ability", 30, ability_effect="stun", ability_value=0, ability_duration=1),
            _action("heavy_attack", 20, "low"),
        ],
    },
]

FLOOR_4_MINI_BOSS: EnemyDef = {
    "name": "Iron Colossus",
    "hp": 200, "speed": 7, "attack": 22, "defense": 12,
    "xp": 350, "gold_min": 90, "gold_max": 130,
    "action_table": [
        _action("basic_attack", 40, "high"),
        _action("heavy_attack", 35, "high"),
        _action("defend", 25, "high"),
        _action("heavy_attack", 55, "low"),
        _action("ability", 30, "low", ability_effect="shatter", ability_value=35, ability_duration=2),
        _action("ability", 15, "low", ability_effect="stun", ability_value=0, ability_duration=1),
    ],
}

# ─── Floor 5 ──────────────────────────────────────────────────────────────────

FLOOR_5_ENEMIES: list[EnemyDef] = [
    {
        "name": "Void Shade",
        "hp": 75, "speed": 14, "attack": 20, "defense": 5,
        "xp": 65, "gold_min": 22, "gold_max": 38,
        "action_table": [
            _action("basic_attack", 40),
            _action("ability", 40, ability_effect="decay", ability_value=8, ability_duration=3),
            _action("heavy_attack", 20, "low"),
        ],
    },
    {
        "name": "Cursed Mage",
        "hp": 68, "speed": 11, "attack": 22, "defense": 4,
        "xp": 68, "gold_min": 24, "gold_max": 40,
        "action_table": [
            _action("basic_attack", 30),
            _action("ability", 50, ability_effect="burn", ability_value=10, ability_duration=3),
            _action("heavy_attack", 20, "low"),
        ],
    },
    {
        "name": "Bone Dragon Whelp",
        "hp": 90, "speed": 10, "attack": 19, "defense": 8,
        "xp": 72, "gold_min": 26, "gold_max": 44,
        "action_table": [
            _action("basic_attack", 50, "high"),
            _action("heavy_attack", 30, "high"),
            _action("ability", 20, "high", ability_effect="frostbite", ability_value=8, ability_duration=2),
            _action("heavy_attack", 50, "low"),
            _action("ability", 50, "low", ability_effect="stun", ability_value=0, ability_duration=1),
        ],
    },
]

FLOOR_5_MINI_BOSS: EnemyDef = {
    "name": "The Lich",
    "hp": 250, "speed": 10, "attack": 26, "defense": 10,
    "xp": 450, "gold_min": 110, "gold_max": 160,
    "action_table": [
        _action("basic_attack", 25, "high"),
        _action("ability", 45, "high", ability_effect="decay", ability_value=10, ability_duration=3),
        _action("heavy_attack", 30, "high"),
        _action("heavy_attack", 40, "low"),
        _action("ability", 35, "low", ability_effect="silence", ability_value=0, ability_duration=2),
        _action("ability", 25, "low", ability_effect="fear", ability_value=0, ability_duration=2),
    ],
}

# ─── Floor 6 ──────────────────────────────────────────────────────────────────

FLOOR_6_ENEMIES: list[EnemyDef] = [
    {
        "name": "Abyss Crawler",
        "hp": 95, "speed": 13, "attack": 24, "defense": 7,
        "xp": 82, "gold_min": 28, "gold_max": 48,
        "action_table": [
            _action("basic_attack", 40),
            _action("ability", 40, ability_effect="decay", ability_value=10, ability_duration=3),
            _action("heavy_attack", 20, "low"),
        ],
    },
    {
        "name": "Mirror Wraith",
        "hp": 80, "speed": 16, "attack": 22, "defense": 5,
        "xp": 78, "gold_min": 26, "gold_max": 44,
        "action_table": [
            _action("basic_attack", 50),
            _action("ability", 30, ability_effect="confuse", ability_value=0, ability_duration=2),
            _action("heavy_attack", 20, "low"),
        ],
    },
    {
        "name": "Ruin Sentinel",
        "hp": 110, "speed": 8, "attack": 26, "defense": 14,
        "xp": 88, "gold_min": 30, "gold_max": 52,
        "action_table": [
            _action("basic_attack", 40, "high"),
            _action("defend", 30, "high"),
            _action("heavy_attack", 30, "high"),
            _action("heavy_attack", 60, "low"),
            _action("ability", 40, "low", ability_effect="shatter", ability_value=40, ability_duration=2),
        ],
    },
]

FLOOR_6_MINI_BOSS: EnemyDef = {
    "name": "Chaos Hydra",
    "hp": 310, "speed": 11, "attack": 30, "defense": 12,
    "xp": 560, "gold_min": 140, "gold_max": 200,
    "action_table": [
        _action("basic_attack", 30, "high"),
        _action("heavy_attack", 40, "high"),
        _action("ability", 30, "high", ability_effect="poison", ability_value=12, ability_duration=3),
        _action("heavy_attack", 40, "low"),
        _action("ability", 35, "low", ability_effect="weaken", ability_value=30, ability_duration=3),
        _action("ability", 25, "low", ability_effect="stun", ability_value=0, ability_duration=1),
    ],
}

# ─── Floor 7 ──────────────────────────────────────────────────────────────────

FLOOR_7_ENEMIES: list[EnemyDef] = [
    {
        "name": "Oblivion Knight",
        "hp": 120, "speed": 12, "attack": 30, "defense": 14,
        "xp": 100, "gold_min": 35, "gold_max": 58,
        "action_table": [
            _action("basic_attack", 40, "high"),
            _action("heavy_attack", 35, "high"),
            _action("defend", 25, "high"),
            _action("heavy_attack", 60, "low"),
            _action("ability", 40, "low", ability_effect="weaken", ability_value=30, ability_duration=2),
        ],
    },
    {
        "name": "Eternity Specter",
        "hp": 100, "speed": 17, "attack": 28, "defense": 6,
        "xp": 95, "gold_min": 32, "gold_max": 54,
        "action_table": [
            _action("basic_attack", 40),
            _action("ability", 40, ability_effect="drain_mana", ability_value=15, ability_duration=3),
            _action("heavy_attack", 20, "low"),
        ],
    },
    {
        "name": "Void Titan",
        "hp": 140, "speed": 9, "attack": 32, "defense": 16,
        "xp": 110, "gold_min": 38, "gold_max": 62,
        "action_table": [
            _action("basic_attack", 35, "high"),
            _action("heavy_attack", 40, "high"),
            _action("defend", 25, "high"),
            _action("heavy_attack", 55, "low"),
            _action("ability", 45, "low", ability_effect="decay", ability_value=12, ability_duration=3),
        ],
    },
]

FLOOR_7_MINI_BOSS: EnemyDef = {
    "name": "The Dread Archon",
    "hp": 380, "speed": 13, "attack": 36, "defense": 16,
    "xp": 700, "gold_min": 180, "gold_max": 260,
    "action_table": [
        _action("basic_attack", 25, "high"),
        _action("heavy_attack", 40, "high"),
        _action("ability", 35, "high", ability_effect="fear", ability_value=0, ability_duration=2),
        _action("heavy_attack", 45, "low"),
        _action("ability", 35, "low", ability_effect="decay", ability_value=14, ability_duration=3),
        _action("ability", 20, "low", ability_effect="silence", ability_value=0, ability_duration=2),
    ],
}

# ─── Floor 8 — Final Boss ─────────────────────────────────────────────────────

FINAL_BOSS: EnemyDef = {
    "name": "The Abyss Sovereign",
    "hp": 500, "speed": 14, "attack": 42, "defense": 18,
    "xp": 1000, "gold_min": 300, "gold_max": 500,
    "action_table": [
        _action("basic_attack", 20, "high"),
        _action("heavy_attack", 35, "high"),
        _action("ability", 25, "high", ability_effect="decay", ability_value=15, ability_duration=3),
        _action("ability", 20, "high", ability_effect="weaken", ability_value=30, ability_duration=3),
        _action("heavy_attack", 40, "low"),
        _action("ability", 30, "low", ability_effect="stun", ability_value=0, ability_duration=1),
        _action("ability", 20, "low", ability_effect="fear", ability_value=0, ability_duration=2),
        _action("ability", 10, "low", ability_effect="silence", ability_value=0, ability_duration=2),
    ],
}

# ─── Lookup helpers ───────────────────────────────────────────────────────────

ENEMIES_BY_FLOOR: dict[int, list[EnemyDef]] = {
    1: FLOOR_1_ENEMIES,
    2: FLOOR_2_ENEMIES,
    3: FLOOR_3_ENEMIES,
    4: FLOOR_4_ENEMIES,
    5: FLOOR_5_ENEMIES,
    6: FLOOR_6_ENEMIES,
    7: FLOOR_7_ENEMIES,
    8: [],  # floor 8 is final boss only
}

MINI_BOSSES: dict[int, EnemyDef] = {
    1: FLOOR_1_MINI_BOSS,
    2: FLOOR_2_MINI_BOSS,
    3: FLOOR_3_MINI_BOSS,
    4: FLOOR_4_MINI_BOSS,
    5: FLOOR_5_MINI_BOSS,
    6: FLOOR_6_MINI_BOSS,
    7: FLOOR_7_MINI_BOSS,
}
