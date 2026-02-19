# Arcane Depths — Tech Architecture

## Stack Summary
| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI |
| LLM Orchestration | LangGraph |
| Frontend | Next.js |
| State Management | Zustand |
| Database | SQLite (dev) → PostgreSQL (prod) |
| Auth | OAuth via Google / GitHub |
| LLM Provider | Groq (free tier) / Gemini Flash (cheap) / Ollama (local) — swappable via env var |
| Streaming | Server-Sent Events (SSE) |

---

## Backend — FastAPI + LangGraph

### LangGraph Workflow Graphs

**Spell Synthesis Graph**
```
[Check Grimoire DB]
     ├── (hit, no luck roll) → [Return cached spell]
     ├── (hit, luck roll succeeds) → [Check variant thresholds] → [Player chooses variant or new discovery]
     └── (miss / new variant) → [Call LLM in JSON mode]
                                    → [Pydantic validation]
                                         → (fail ×3) → [Return fallback spell]
                                         → (pass) → [Effect normalization (keyword classifier)]
                                                   → [Stat sanitization (damage formula)]
                                                   → [Content moderation filter]
                                                   → [Save to Grimoire DB]
                                                   → [Return spell]
```

**Combat Narration Graph**
```
[Speed check → determine turn order + extra actions]
     → [Pre-damage hooks (reflect, shield)]
     → [Resolve actions in order]
     → [Tick all status effects]
     → [Build narration prompt with full context]
     → [Stream LLM narration via SSE]
     → [Check phase transition] → (yes) → [Generate boss phase narration]
```

**Room Generation Graph**
```
[Determine event type (weighted random by floor)]
     → [Generate room description via LLM]
     → [Return room + event type]
```

**Shrine Graph**
```
[Roll 3 outcomes server-side (buff / curse / neutral)]
     → [Generate 3 ambiguous flavor descriptions via LLM]
     → [Player picks one]
     → [Reveal and apply outcome]
```

### Game Logic Engine (Pure Python, No LLM)
- Turn resolution, Speed comparison, stat calculations
- Status effect application and tick-down each turn
- Danger meter increments
- Loot table rolls (chest contents, enemy drops, ingredient tier weighting)
- XP grants and level-up triggers
- Shop inventory generation and pricing

### Database Schema (SQLite / PostgreSQL)
```sql
-- Global spell registry
grimoire (
  ingredient_key TEXT,       -- sorted combo hash
  variant_index  INTEGER,    -- 0 = base, 1+ = luck variants
  spell_name     TEXT,
  flavor_text    TEXT,
  stats_json     JSON,       -- damage, mana_cost, cooldown, damage_type
  effects_json   JSON,       -- list of effect primitives
  ingredient_tiers JSON,
  luck_threshold INTEGER,    -- 0 for base; discoverer's Luck for variants
  discovered_by  TEXT,
  discovered_at  TIMESTAMP,
  PRIMARY KEY (ingredient_key, variant_index)
)

-- Active and historical runs
runs (
  id          UUID PRIMARY KEY,
  player_id   TEXT,
  class       TEXT,
  state_json  JSON,          -- full game state snapshot
  floor       INTEGER,
  status      TEXT,          -- active | dead | victory
  created_at  TIMESTAMP,
  updated_at  TIMESTAMP
)

-- Player accounts
players (
  oauth_id          TEXT PRIMARY KEY,
  username          TEXT,
  provider          TEXT,    -- google | github
  legacy_spellbook  JSON,    -- list of up to 5 banked spells
  grimoire_count    INTEGER, -- number of spells first-discovered
  created_at        TIMESTAMP
)
```

### Session Management
- Each run = UUID session; full game state stored in `runs.state_json`
- State includes: HP, Mana, all stats, floor, danger meter, action count, inventory, spell collection, equipment, active status effects

### LLM Provider Abstraction
```python
# Swappable via LLM_PROVIDER env var
class LLMClient:
    def complete(self, prompt, json_mode=False) -> str: ...
    def stream(self, prompt) -> Iterator[str]: ...

# Implementations: GroqClient, GeminiClient, OllamaClient
```

### Security & Rate Limiting
- OAuth token verification on all authenticated endpoints
- Rate limit on `/forge`: max 20 new spell discoveries per user per hour
- Content moderation filter on all Grimoire writes (spell name + flavor text)

---

## Frontend — Next.js + Zustand

### Zustand Stores
| Store | Contents |
|-------|----------|
| `useGameStore` | HP, Mana, all stats, gold, floor, danger meter, action count, spell collection, ingredient inventory, equipment, XP/level |
| `useGrimoireStore` | Locally cached Grimoire entries for the session |
| `useCombatStore` | Enemy HP, turn log, streaming narration buffer, active status effects (player + enemy) |
| `useLegacyStore` | Banked spells, selected starting spells for current run |

### UI Panels
- **Narrative Log** — Scrollable text; LLM narration streamed token-by-token
- **Action Menu** — Contextual buttons: Explore / Cast Spell / Use Item / Defend / Flee / Open Chest / Visit Shop / Challenge Boss
- **Spell Forge** — Ingredient selection → preview → synthesize
- **Status Bar** — Active effects on player + enemy with turn countdowns (`🔥 Burn 2t | ⚡ Haste 1t`)
- **HUD** — HP, Mana, Speed, Danger Meter, Gold, Floor, XP/Level
- **Grimoire Browser** — Global, searchable, filterable by tier; shows discoverer + Luck threshold for variants
- **Legacy Spellbook** — View banked spells; select up to 3 for next run
- **Floor Map** — Simple visual: explored rooms, chest locations, danger level

### Streaming
- Backend streams LLM tokens via SSE
- Frontend appends tokens to Narrative Log in real time

---

## API Endpoints
```
POST /api/auth/login              → OAuth redirect
GET  /api/auth/me                 → player profile + legacy spellbook

POST /api/run/start               → new run (class + starting legacy spells)
GET  /api/run/{id}/state          → full game state
POST /api/run/{id}/explore        → take exploration action → room + event
POST /api/run/{id}/shrine         → get 3 choices; POST choice → apply outcome
POST /api/run/{id}/combat/action  → submit action → streams narration via SSE
POST /api/run/{id}/forge          → synthesize spell (Grimoire check + LLM if new)
POST /api/run/{id}/boss           → initiate mini-boss or final boss
POST /api/run/{id}/victory        → bank spell to legacy spellbook

GET  /api/grimoire                → all spells (paginated, filterable by tier/name)
GET  /api/grimoire/{key}          → specific spell by ingredient combo + variant
```

---

## Development Phases
| Phase | Focus |
|-------|-------|
| 1 | Core loop: scaffolding, OAuth, run creation, exploration, combat (no LLM), death/reset |
| 2 | LLM integration: LangGraph, narration SSE, room gen, shrine, spell synthesis + Grimoire |
| 3 | Validation pipeline: Pydantic, retry logic, effect classifier, damage formula, effect engine, status bar UI |
| 4 | Spell Forge & ingredients: tier system, acquisition, inventory, Forge UI, Grimoire browser |
| 5 | Full dungeon: all 8 floors, mini-bosses, final boss, shops, chests, gold economy |
| 6 | Meta-progression & polish: Legacy Spellbook, equipment, leveling UI, leaderboard, mobile UI |
