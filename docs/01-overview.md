# Arcane Depths — Overview & Core Concept

## What It Is
A text-based roguelike dungeon crawler where players descend 8 floors of a procedurally narrated dungeon, collecting **word-concept ingredients** to synthesize unique spells via an LLM.

## Core Pillars
1. **Spell Crafting** — Combine word ingredients to create spells; the LLM invents the spell on first discovery
2. **Risk/Reward Exploration** — A Danger Meter rises as you explore; more loot = more danger
3. **Shared Global Grimoire** — Every spell discovered by any player is permanently canonical for all players
4. **Meta-Progression** — Win a run → bank a spell → start future runs stronger

## Tech Stack
- **Backend**: Python, FastAPI, LangGraph
- **Frontend**: Next.js, Zustand
- **Database**: SQLite (dev) → PostgreSQL (prod)
- **Auth**: OAuth (Google / GitHub)
- **LLM**: Model-agnostic; targets Groq (free tier), Gemini Flash (cheap), or Ollama (local)

## Classes
| Class | Focus | Starting Ingredients | Unique Mechanic |
|-------|-------|---------------------|-----------------|
| 🛡️ Knight | Physical skills, durability | `Iron`, `Shield`, `Charge`, `Blood` (Basic) | Equip Stances (passive modifiers) |
| 🔮 Mage | Spell power, versatility | `Fire`, `Time`, `Void`, `Mirror` (Basic/Rare) | Higher Rare/Legendary ingredient drop chance |

> Future classes: Rogue, Shaman

## Win / Loss
- **Win**: Defeat the Floor 8 final boss → victory screen + LLM epilogue + bank 1 spell to Legacy Spellbook
- **Loss**: HP reaches 0 → death screen with full run stats (floor, kills, gold, damage, cause of death)
