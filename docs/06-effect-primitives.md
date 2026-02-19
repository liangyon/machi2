# Arcane Depths — Effect Primitive Library

All spell effects are composed from a fixed library of primitives. The LLM describes effects in plain English; the backend keyword classifier maps them to these primitives. Complex effects are combinations of primitives.

## Damage-over-Time
| Primitive | Description |
|-----------|-------------|
| `burn(n)` | X fire damage/turn for N turns |
| `bleed(n)` | X physical damage/turn for N turns |
| `poison(n)` | X poison damage/turn for N turns (stacks) |
| `decay(n)` | X void damage/turn for N turns; also reduces max HP |
| `frostbite(n)` | X cold damage/turn for N turns |

## Crowd Control
| Primitive | Description |
|-----------|-------------|
| `stun(n)` | Target skips N turns |
| `slow(n)` | Target acts every other turn for N turns |
| `silence(n)` | Target cannot cast spells for N turns |
| `root(n)` | Target cannot flee for N turns |
| `confuse(n)` | Target attacks randomly (self or opponent) for N turns |
| `fear(n)` | Target skips turn and takes bonus damage for N turns |

## Stat Modifiers
| Primitive | Description |
|-----------|-------------|
| `weaken(n)` | Reduces target Strength by X% for N turns |
| `shatter(n)` | Reduces target Defense by X% for N turns |
| `drain_mana(n)` | Reduces target Mana by X/turn for N turns |
| `empower(n)` | Increases caster Strength/Arcane Affinity by X% for N turns |
| `fortify(n)` | Increases caster Defense by X% for N turns |
| `haste(n)` | Caster Speed increased significantly for N turns (may grant extra actions) |

## Recovery
| Primitive | Description |
|-----------|-------------|
| `lifesteal(pct)` | Caster heals for PCT% of damage dealt |
| `regen(n)` | Caster restores X HP/turn for N turns |
| `mana_regen(n)` | Caster restores X Mana/turn for N turns |
| `shield(x)` | Caster gains X temporary HP (absorbs damage first) |

## Special / Exotic (Rare/Legendary/Conceptual tier only)
| Primitive | Description |
|-----------|-------------|
| `echo(n)` | Repeats caster's last spell for free after N turns |
| `freeze_danger(n)` | Danger Meter stops rising for N exploration actions |
| `curse_mark(n)` | Target takes X% more damage from all sources for N turns |
| `soul_link(n)` | Damage dealt to target also damages caster by X% for N turns (high risk/reward) |
| `nullify(n)` | Removes all status effects from target (offensive or defensive) |
| `reflect(n)` | Next N attacks against caster are reflected back at attacker |
| `time_stop(n)` | = `stun(n)` + `freeze_danger(n)` |
| `memory(n)` | Stores current HP/Mana; restores them after N turns (Conceptual tier only) |
| `unravel(n)` | Strips all stat buffs from target; deals damage equal to stripped value |

## Composite Effect Examples
| Spell | Ingredients | Composed From |
|-------|-------------|---------------|
| *Slow Burn* | Fire + Time | `burn(3)` + `slow(2)` |
| *Time Stop* | Time + Void | `stun(2)` + `freeze_danger(1)` |
| *Soul Drain* | Dark + Hunger | `lifesteal(30%)` + `weaken(2)` |
| *Heroic Echo* | Heroic + Echo | `empower(3)` + `echo(1)` |
| *Grief's Weight* | Grief + Stone | `slow(3)` + `shatter(2)` + `fear(1)` |

## Implementation Notes
- **`haste(n)`**: Increases Speed stat temporarily; re-evaluate turn order each turn while active. Define whether it can stack.
- **`echo(n)`**: Requires storing last-cast spell in session state. Edge cases: no previous spell, spell on cooldown, consumable used.
- **`memory(n)`**: Needs ruling — does it prevent death during the N-turn window?
- **`reflect(n)`**: Handled in the pre-damage hook step of turn resolution.
- **`time_stop`**: Crosses combat/exploration boundary — requires shared floor state object.
- **Effect stacking**: `poison` stacks; most others refresh duration. Define caps per effect.
- **Keyword classifier**: Log all unmatched LLM effect strings for ongoing expansion. Consider fuzzy matching as fallback.
