# Arcane Depths — Floor Structure & Exploration

## Dungeon Layout
- 8 floors total; floors 1–7 each have a mini-boss; floor 8 is the final boss
- Each floor is explored via **Exploration Actions**

## Action Economy
- Each floor starts with a pool of **10–15 Exploration Actions**
- Each action = entering a new room (LLM generates description + event)
- **After the pool is exhausted**: player may keep exploring, but each additional action raises the Danger Meter by an extra tier increment (escalating risk/reward)
- The mini-boss can be challenged **at any time**

## Room Events (weighted random per floor)
| Event | Description |
|-------|-------------|
| Enemy encounter | Fight for gold + XP; rare chance of ingredient drop |
| Chest | Costs gold to open → random ingredient from floor pool + possible loot |
| Shop | Spend gold on guaranteed ingredients, potions, equipment |
| Shrine | Pick 1 of 3 ambiguous LLM-generated events (buff or curse) |
| Empty room | Flavor text only |

## Danger Meter
| Tier | Level | Effect |
|------|-------|--------|
| 1 | 0–30% | Normal enemies |
| 2 | 31–60% | Enemies +20% stats |
| 3 | 61–85% | Elite enemies appear; mini-boss gains a buff |
| 4 | 86–100% | Enemies brutal; mini-boss empowered |

Danger rises with each action. Beyond the action pool, each extra action adds a full tier increment.

## Shrine System
- Outcomes are **pre-rolled server-side** (buff / curse / neutral) before LLM generates flavor
- LLM generates 3 ambiguous choice labels + 1-sentence descriptions (e.g. *"A chalice of black wine"*)
- Player picks one → outcome revealed and applied
- Possible outcomes: stat buff, stat curse, free ingredient, HP drain, mana restore, etc.

## Shop System
- 1 shop per floor with **4–6 fixed items**: 2 ingredients (floor-appropriate tier), 2 potions, 1–2 equipment
- Prices scale with floor + item tier (e.g. Basic ingredient floor 1: ~30g; Legendary floor 7: ~300g)
- Player can **re-roll shop inventory** for gold (scales ~50–150g per floor); re-roll regenerates all slots
- Shop does **not** refresh between visits on the same floor

## Gold Economy
- Enemies drop gold on defeat + small chance of rare ingredient drop
- Gold uses: open chests, buy from shop, re-roll shop
- Gold resets to 0 on death (no carry-over between runs)
