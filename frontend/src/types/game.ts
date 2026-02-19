// ─── Core Game Types ──────────────────────────────────────────────────────────

export interface StatusEffect {
  name: string;
  emoji: string;
  turnsRemaining: number;
  description: string;
}

export interface GameState {
  hp: number;
  maxHp: number;
  mana: number;
  maxMana: number;
  speed: number;
  attack: number;
  defense: number;
  luck: number;
  gold: number;
  floor: number;
  dangerMeter: number;
  actionCount: number;
  xp: number;
  level: number;
  inventory: InventoryItem[];
  spellCollection: Spell[];
  equipment: Equipment;
  activeStatusEffects: StatusEffect[];
  // Phase 1 additions
  arcaneAffinity: number;
  strength: number;
  actionPool: number;
  unspentStatPoints: number;
  currentEnemy: EnemyState | null;
  shopInventory: ShopItem[];
  rolledShrineOutcomes: ShrineOutcome[];
  ingredientInventory: InventoryItem[];
  consumables: ConsumableItem[];
  kills: number;
  causeOfDeath: string | null;
}

export interface InventoryItem {
  id: string;
  name: string;
  type: "ingredient" | "consumable";
  tier: number;
  quantity: number;
}

export interface SpellStats {
  damage: number;
  manaCost: number;
  cooldown: number;
  damageType: string;
}

export interface Spell {
  ingredientKey: string;
  variantIndex: number;
  spellName: string;
  flavorText?: string;
  stats: SpellStats;
  effects: EffectPrimitive[];
  ingredientTiers: Record<string, number>;
  luckThreshold: number;
  discoveredBy?: string;
  discoveredAt?: string;
}

export interface EffectPrimitive {
  type: string;
  value: number;
  duration?: number;
  target?: "player" | "enemy";
}

export interface Equipment {
  weapon?: string;
  armor?: string;
  accessory?: string;
}

// ─── Phase 1 new types ────────────────────────────────────────────────────────

export interface EnemyState {
  name: string;
  hp: number;
  max_hp: number;
  speed: number;
  attack: number;
  defense: number;
  xp: number;
  gold_min: number;
  gold_max: number;
  active_status_effects: StatusEffect[];
}

export interface ShopItem {
  id: string;
  name: string;
  type: "ingredient" | "consumable" | "equipment";
  tier: string;
  price: number;
  ingredient_id: string | null;
  effect: string | null;
  stat_bonus?: Record<string, number>;
  slot?: string;
}

export interface ShrineOutcome {
  type: "buff" | "curse" | "neutral";
  effect: string;
  description: string;
}

export interface ConsumableItem {
  id: string;
  name: string;
  type: "consumable";
  tier: string;
  effect: string;
  quantity: number;
}

// ─── Run ──────────────────────────────────────────────────────────────────────

export type RunStatus = "active" | "dead" | "victory";

export interface Run {
  id: string;
  playerClass: string;
  state: GameState;
  floor: number;
  status: RunStatus;
}

// ─── Combat ───────────────────────────────────────────────────────────────────

export interface Enemy {
  name: string;
  hp: number;
  maxHp: number;
  speed: number;
  activeStatusEffects: StatusEffect[];
}

export interface TurnLogEntry {
  actor: "player" | "enemy";
  action: string;
  damage?: number;
  effect?: string;
}

// ─── Grimoire ─────────────────────────────────────────────────────────────────

export interface GrimoireEntry extends Spell {
  ingredientKey: string;
  variantIndex: number;
}

// ─── Shrine ───────────────────────────────────────────────────────────────────

export interface ShrineChoice {
  id: number;
  flavor: string;
}

// ─── Room ─────────────────────────────────────────────────────────────────────

export type EventType = "empty" | "enemy" | "chest" | "shrine" | "shop" | "boss";

export interface Room {
  description: string;
  eventType: EventType;
}
