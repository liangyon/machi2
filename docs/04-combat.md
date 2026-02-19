# Arcane Depths — Combat System

## Structure
- Turn-based: player acts → enemy acts → status effects tick → check win/loss
- Player action menu:
  - Cast a spell (from collection; shows mana cost; greyed out if on cooldown with turn counter)
  - Use a class skill
  - Use a consumable (HP Potion / Mana Potion)
  - Defend (reduce incoming damage this turn)
  - Flee (costs 1 exploration action; may fail at high Danger)

## Turn Resolution Order
1. **Speed check** — compare player Speed vs enemy Speed to determine who acts first; if player Speed ≥ enemy Speed × 1.5, player gets 1 extra action this turn (and vice versa for fast enemies)
2. **Pre-damage hooks** — check `reflect` (redirect incoming), `shield` (absorb damage)
3. **First actor's action** — apply damage + effects
4. **Second actor's action** — apply damage + effects (skipped if stunned/dead)
5. **Extra action** (if Speed threshold met) — the faster combatant takes a bonus action
6. **Status effect ticks** — all active DoT, CC, and stat mod effects tick down on both sides
7. **Status bar update** — UI refreshes active effects with remaining durations
8. **Win/loss check** — HP ≤ 0 triggers end of combat

## Status Bar
- Displayed for both player and enemy
- Format: `🔥 Burn 2t | 🧊 Slow 1t | 🛡️ Shield 45HP`
- Expired effects removed automatically each tick

## LLM Narration
- After full turn resolution, LLM generates **2–3 sentence dramatic narration**
- Context passed: class, level, action taken, spell name, enemy name/type, HP states, active statuses, floor, danger tier
- Streamed token-by-token via SSE for dramatic effect
- Mini-boss phase transition (at 50% HP) triggers a special narration call
- Final boss uses a wide randomized attack pool — LLM narrates each new attack dramatically

## Enemy AI
- Each enemy has a **weighted action table**: named attacks with probabilities that shift by HP bracket
  - e.g. at >50% HP: 60% basic attack, 30% ability, 10% defend
  - at <50% HP: 30% basic attack, 50% heavy attack, 20% ability
- Enemy attacks use the same **effect primitive system** as player spells (can apply burn, stun, weaken, etc.)
- Mini-bosses: scripted phase patterns; phase 2 unlocks new attacks at 50% HP
- Final boss: large randomized arsenal; players must adapt each run

## Spell Cooldown Display
- Spells on cooldown shown as greyed out: `🔒 Slow Burn — 2 turns`
- Active spells show mana cost next to name
