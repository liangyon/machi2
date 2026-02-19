# Arcane Depths — Open Questions & Future Decisions

Items that are intentionally deferred. Resolve before the relevant development phase.

## Before Phase 3 (Effect Engine)
- **Effect stacking rules**: Does `burn` stack from multiple spells? (Likely yes with a per-effect cap)
- **`haste(n)` scoping**: Does the extra action allow casting a second spell? Does it trigger a second narration call? Can it stack?
- **`echo(n)` edge cases**: What if no previous spell exists? What if the echoed spell is on cooldown?
- **`memory(n)` death ruling**: Does it prevent death during the N-turn window, or just restore HP/Mana after?
- **Speed threshold tuning**: What exact multiplier triggers an extra action? (Currently ×1.5 — needs playtesting)

## Before Phase 5 (Full Dungeon)
- **Enemy roster content pass**: Full list of enemies per floor — names, types, HP ranges, gold drops, XP values, action tables, ingredient drop pools
- **Mini-boss roster**: 7 mini-bosses (floors 1–7) — names, types, phase 1 + phase 2 attack sets, lore
- **Final boss design**: Attack pool size, phase count, any unique mechanics beyond randomized arsenal
- **Elemental interactions**: Type chart (Fire 2× vs undead) vs flat defense bypass — to be designed
- **Ingredient rarity gating**: Are Legendary ingredients class-exclusive or purely floor-gated?
- **Cursed spells**: Can they be cleansed at a shrine, or are they permanent for the run?

## Before Phase 6 (Polish)
- **Luck variant probability tuning**: `P = base_chance / (1 + existing_variants)` — what is `base_chance`? Needs playtesting.
- **Legacy Spellbook balance**: Are there restrictions on which spells can be banked (e.g. no Conceptual tier)?
- **Equipment system detail**: What specific weapons/armor/accessories exist? Do any have special effects beyond flat stat bonuses?
- **Consumable expansion**: Scrolls (one-use spells), bombs, antidotes — design and balance

## Future / Post-Launch
- **Rogue class**: Stealth, trap-setting, ingredient theft from enemies
- **Shaman class**: Summons, nature magic, healing focus
- **Effect primitive expansion**: `summon`, `transform`, `duplicate` — design when base system is stable
- **Leaderboard design**: What metric ranks players? (Floor reached? Damage dealt? Grimoire discoveries?)
- **Multiplayer Grimoire social features**: Discoverer profiles, most-discovered players, rarest spell leaderboard
