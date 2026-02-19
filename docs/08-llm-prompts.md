# Arcane Depths — LLM Prompt Templates

All prompts are model-agnostic and return structured JSON (or streamed narrative text).

---

## Spell Synthesis Prompt
Used when a new ingredient combo (or variant) is discovered. Returns JSON.

```
You are the arcane engine of a fantasy roguelike called Arcane Depths.
The player has combined: [{INGREDIENT_1} (tier: {TIER_1}), {INGREDIENT_2} (tier: {TIER_2})].
Player class: {CLASS}. Player level: {LEVEL}. Floor: {FLOOR}/8.
{VARIANT_HINT}

Tier scale: Basic < Rare < Legendary < Conceptual. Scale creativity and power accordingly.

Generate a spell as valid JSON:
{
  "name": "string",
  "flavor_text": "string (1-2 evocative sentences)",
  "damage_type": "fire | cold | arcane | physical | poison | void | light | dark | conceptual",
  "base_damage": [min_int, max_int],
  "mana_cost": int,
  "cooldown_turns": int,
  "effects": ["plain English description of each effect beyond direct damage"]
}

Examples of effects: "burns the target over time", "slows the enemy", "heals the caster for a portion of damage dealt".
Output only valid JSON. Be creative and thematic.
```

`{VARIANT_HINT}` for variant discovery: `"This is a variant of an existing spell for this combo. Make it more powerful or exotic than the base version."`

---

## Combat Narration Prompt
Used after every turn resolution. Streamed as plain text.

```
You are narrating a turn in a fantasy dungeon battle.
Player: {CLASS} (level {LEVEL}), HP {HP}/{MAX_HP}, Speed {SPEED}
Action: {ACTION_TYPE} — {SPELL_OR_SKILL_NAME}
Enemy: {ENEMY_NAME} (type: {ENEMY_TYPE}), HP {ENEMY_HP}/{ENEMY_MAX_HP}, Speed {ENEMY_SPEED}
Active effects — Player: {PLAYER_STATUSES}. Enemy: {ENEMY_STATUSES}.
Outcome: dealt {DAMAGE} {DAMAGE_TYPE} damage. New enemy HP: {NEW_ENEMY_HP}.
Floor: {FLOOR}. Danger: {DANGER_TIER}.
{EXTRA_ACTION_NOTE}

Write 2–3 sentences of vivid, dramatic narration. Be concise but evocative. No dialogue.
```

`{EXTRA_ACTION_NOTE}` if Speed advantage triggered: `"The player's superior speed allowed them to strike again."`

---

## Boss Phase Transition Prompt
Used when a mini-boss or final boss crosses 50% HP. Streamed as plain text.

```
You are narrating a dramatic phase transition in a boss battle.
Boss: {BOSS_NAME}, now at {HP}/{MAX_HP} HP.
Floor: {FLOOR}. The boss has just entered its second phase.

Write 3–4 sentences describing the boss's transformation or power surge. Be dramatic and ominous.
```

---

## Room Generation Prompt
Used when a player explores a new room. Returns plain text (2 sentences).

```
You are generating a room description for floor {FLOOR} of a dark fantasy dungeon.
Event type: {EVENT_TYPE} (combat | chest | shop | shrine | empty).
Danger level: {DANGER_TIER}.

Write 2 sentences describing what the player sees as they enter. Be atmospheric and specific.
```

---

## Shrine Prompt
Used when a player encounters a shrine. Returns JSON array.

```
You are generating 3 mysterious shrine offerings for a dark fantasy dungeon on floor {FLOOR}.
Each offering should sound ambiguous — it could be a blessing or a curse. Do not reveal the outcome.

Return valid JSON:
[
  {"label": "short evocative name", "description": "1 sentence, mysterious tone"},
  {"label": "...", "description": "..."},
  {"label": "...", "description": "..."}
]
```

---

## Victory Epilogue Prompt
Used after the final boss is defeated. Streamed as plain text.

```
You are writing the ending narration for a victorious run in a dark fantasy roguelike.
Player: {CLASS} (level {LEVEL}), defeated the final boss on floor 8.
Spells used this run: {SPELL_LIST}.
Most used spell: {TOP_SPELL}.

Write a 3–4 sentence narrative epilogue for this character's victory. Be evocative and personal to their build.
```

---

## JSON Validation Error Correction Prompt
Used by LangGraph retry logic when Pydantic parsing fails.

```
Your previous response was invalid JSON or missing required fields.
Required fields: name, flavor_text, damage_type, base_damage, mana_cost, cooldown_turns, effects.
Error: {PARSE_ERROR}

Please try again and output only valid JSON matching the required schema.
```
