# Arcane Depths — Spell System & Grimoire

## Ingredient Tiers
| Tier | Rarity | Examples | Where Found |
|------|--------|----------|-------------|
| **Basic** | Common | `Fire`, `Ice`, `Water`, `Earth`, `Wind`, `Stone`, `Iron`, `Blood`, `Shadow`, `Lightning` | Chests (all floors), Shops (all floors) |
| **Rare** | Uncommon | `Light`, `Dark`, `Storm`, `Plague`, `Mirror`, `Time`, `Frost`, `Venom` | Chests (floors 3+), Shops (floors 4+), rare enemy drops |
| **Legendary** | Very Rare | `Void`, `Abyss`, `Eternity`, `Ruin`, `Oblivion`, `Chaos` | Chests (floors 6+), boss drops, rare enemy drops (floors 5+) |
| **Conceptual** | Exotic | `Heroic`, `Hunger`, `Echo`, `Grief`, `Triumph`, `Silence`, `Memory` | Shrine rewards, final boss drop, special events only |

- Ingredient inventory capped at **10 slots**
- Mixing tiers is valid; higher tiers → stronger, more exotic spells
- LLM is told ingredient tiers so it scales power appropriately

## Spell Synthesis Flow
1. Player selects 2–3 ingredients in the **Spellforge** (accessible between encounters)
2. Backend checks **Global Grimoire DB** + player's **Luck stat**:
   - Known combo + no Luck roll → return cached spell instantly (no LLM call)
   - Known combo + Luck roll succeeds → may discover a **variant** (see below)
   - New combo → call LLM → validate → save to Grimoire permanently
3. Spell added to player's collection (no slot limit currently)

## Luck-Based Variant System
- Every combo has a **base spell** (first discovery, no stat requirement)
- High Luck triggers a roll for a **variant** — a more powerful/exotic version of the same combo
- Variant probability: `P(variant) = base_chance / (1 + existing_variant_count)` — diminishing returns
- Each variant stores the discoverer's Luck stat; future players need **≥ 80%** of that value to unlock it
- If a player qualifies for multiple variants of the same combo, they **choose** which to craft
- Variants are unlimited per combo but become exponentially rarer to discover

## Global Grimoire
- All discovered spells (base + variants) are **permanently saved** and shared across all players
- Combo key = sorted ingredient hash + variant index
- Grimoire entries store: spell name, flavor text, stats, effects, ingredient tiers, discoverer name, Luck at discovery, timestamp
- **Race condition**: DB `UNIQUE` constraint on `(ingredient_key, variant_index)` with `ON CONFLICT DO NOTHING` — first write wins
- Players can browse the Grimoire (filterable by tier, searchable by name) from the main menu

## LLM Validation Pipeline (Spell Synthesis)
### Layer 1 — JSON Enforcement
- LLM called in **JSON mode**; response parsed against Pydantic model
- On failure: LangGraph retries up to **3 times** with error-correction prompt
- After 3 failures: **fallback spell** returned (pre-defined safe spell for that combo hash)

### Layer 2 — Effect Normalization
- LLM outputs `effects` as plain-English strings (e.g. `"burns the target over time"`)
- Python **keyword classifier** maps strings to canonical effect primitives (no second LLM call)
- Unmatched strings are discarded; unmatched strings logged for classifier expansion

### Layer 3 — Stat Sanitization
```
base_damage = clamp(
    llm_value,
    min = floor_min(floor) * tier_mult * level_factor,
    max = floor_max(floor) * tier_mult * level_factor * luck_bonus
)
```
| Variable | Formula |
|----------|---------|
| `floor_min/max` | Floor 1: 5–15 → Floor 8: 60–120 |
| `tier_mult` | Basic=1.0, Rare=1.4, Legendary=2.0, Conceptual=2.5 (averaged) |
| `level_factor` | `1 + (level - 1) * 0.15` |
| `luck_bonus` | `1 + (luck / 100)` (nudges max upward) |

- `mana_cost`: clamped 5–40
- `cooldown_turns`: clamped 0–3
- Missing values get tier-appropriate defaults

## Content Moderation
- Spell names and flavor text run through a **profanity/content filter** before Grimoire save
- Rate limit on `/forge`: max **20 new discoveries per user per hour** to prevent LLM cost abuse
