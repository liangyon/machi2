# Arcane Depths — Stats & Progression

## Core Stats
| Stat | Description | Primary For |
|------|-------------|-------------|
| **HP** | Health points; reach 0 = run ends | Survival |
| **Mana** | Spent to cast spells; regens +5/turn (modified by Arcane Affinity) | Spell frequency |
| **Strength** | Boosts physical skill damage | Knight |
| **Arcane Affinity** | Boosts spell damage + Mana regen rate | Mage |
| **Defense** | Reduces incoming physical damage | Survivability |
| **Speed** | Determines turn order; high Speed can grant extra actions per turn | Agility / burst |
| **Luck** | Chest loot quality, ingredient tier rolls, rare events, max damage ceiling, variant spell discovery | Spell crafting depth |

## Speed & Turn Order
- At the start of each combat, **Speed** is compared between player and enemy
- **Higher Speed acts first** — if player Speed > enemy Speed, player goes first; otherwise enemy goes first
- **Extra actions**: if player Speed exceeds enemy Speed by a threshold (e.g. ×1.5), the player gets **1 extra action** per turn (can cast a second spell, use an item, or defend again)
- Enemies can also have high Speed — a fast enemy may act twice before the player can respond
- Speed can be boosted by equipment, stat points on level-up, and the `haste(n)` effect primitive
- Knight starts with moderate Speed; Mage starts with low Speed (compensated by spell power)

## Mana Regeneration
- Base: **+5 Mana per turn** at start of player's turn
- Formula: `mana_regen = 5 + floor(arcane_affinity / 10)`
- Mana is **not** restored between combats — only potions and `mana_regen` effects restore it mid-run
- Makes Mana a meaningful resource; players can't spam high-cost spells indefinitely

## Leveling Up
- Enemies grant XP; player level starts at **1 each run**
- Design intent: players are **slightly underlevelled** — the gap is bridged by smart spell/skill use
- On level-up: player receives **3 stat points** to freely allocate across any stats
- Max level per run: **10**

## XP Curve
| Level | XP Required | Enemy XP Range |
|-------|-------------|----------------|
| 1→2 | 50 | Floors 1–2: ~15–25 XP/enemy |
| 2→3 | 120 | |
| 3→4 | 220 | |
| 4→5 | 350 | Floors 4–5: ~40–60 XP/enemy |
| 5→6 | 520 | |
| 6→7 | 730 | |
| 7→8 | 990 | Floors 7–8: ~80–110 XP/enemy |
| 8→9 | 1300 | Mini-boss: 150–250 XP |
| 9→10 | 1700 | Final boss: 500 XP |

*A player who fights every enemy will reach level 7–8 by floor 8 — intentionally slightly underlevelled.*

## Equipment
- Found in chests and shops: weapons, armor, accessories
- Provides flat stat bonuses; sometimes includes a bonus word ingredient
- Knight benefits from heavy armor; Mage from staves/robes
- Equipment system detail to be expanded in Phase 6

## Consumables
- **HP Potion** — restores a portion of HP
- **Mana Potion** — restores a portion of Mana
- Found in chests and bought in shops
- Future: scrolls, bombs, antidotes

## Meta-Progression: Legacy Spellbook
- On **victory** (beating floor 8 boss): player banks **1 spell** from their run permanently
- Legacy Spellbook holds up to **5 spells** (player chooses which to replace when full)
- At run start: player may equip **up to 3 banked spells** as starting spells
- Banked spell damage is **clamped to current floor range** to prevent early-floor trivialization
- Tied to OAuth account; persists across all runs
