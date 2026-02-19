import { create } from "zustand";
import { devtools } from "zustand/middleware";
import type { GameState, Run, RunStatus } from "@/types/game";
import { runsApi } from "@/lib/api";

interface GameStore {
  // Run metadata
  runId: string | null;
  playerClass: string | null;
  status: RunStatus | null;

  // Full game state (mirrors backend GameState)
  state: GameState | null;

  // Actions
  setRun: (run: Run) => void;
  updateState: (patch: Partial<GameState>) => void;
  setStatus: (status: RunStatus) => void;
  resetRun: () => void;
  /** Rehydrate full state from server — call on page load if runId is known */
  syncFromServer: (runId: string) => Promise<void>;
}

const defaultGameState: GameState = {
  hp: 100,
  maxHp: 100,
  mana: 50,
  maxMana: 50,
  speed: 10,
  attack: 10,
  defense: 5,
  luck: 5,
  gold: 0,
  floor: 1,
  dangerMeter: 0,
  actionCount: 0,
  xp: 0,
  level: 1,
  inventory: [],
  spellCollection: [],
  equipment: {},
  activeStatusEffects: [],
  arcaneAffinity: 5,
  strength: 10,
  actionPool: 12,
  unspentStatPoints: 0,
  currentEnemy: null,
  shopInventory: [],
  rolledShrineOutcomes: [],
  ingredientInventory: [],
  consumables: [],
  kills: 0,
  causeOfDeath: null,
};

/** Map snake_case backend keys to camelCase frontend keys */
function normalizeState(raw: Record<string, unknown>): GameState {
  return {
    hp: (raw.hp as number) ?? 100,
    maxHp: (raw.max_hp as number) ?? 100,
    mana: (raw.mana as number) ?? 50,
    maxMana: (raw.max_mana as number) ?? 50,
    speed: (raw.speed as number) ?? 10,
    attack: (raw.attack as number) ?? 10,
    defense: (raw.defense as number) ?? 5,
    luck: (raw.luck as number) ?? 5,
    gold: (raw.gold as number) ?? 0,
    floor: (raw.floor as number) ?? 1,
    dangerMeter: (raw.danger_meter as number) ?? 0,
    actionCount: (raw.action_count as number) ?? 0,
    xp: (raw.xp as number) ?? 0,
    level: (raw.level as number) ?? 1,
    inventory: (raw.inventory as GameState["inventory"]) ?? [],
    spellCollection: (raw.spell_collection as GameState["spellCollection"]) ?? [],
    equipment: (raw.equipment as GameState["equipment"]) ?? {},
    activeStatusEffects: (raw.active_status_effects as GameState["activeStatusEffects"]) ?? [],
    arcaneAffinity: (raw.arcane_affinity as number) ?? 5,
    strength: (raw.strength as number) ?? 10,
    actionPool: (raw.action_pool as number) ?? 12,
    unspentStatPoints: (raw.unspent_stat_points as number) ?? 0,
    currentEnemy: (raw.current_enemy as GameState["currentEnemy"]) ?? null,
    shopInventory: (raw.shop_inventory as GameState["shopInventory"]) ?? [],
    rolledShrineOutcomes: (raw.rolled_shrine_outcomes as GameState["rolledShrineOutcomes"]) ?? [],
    ingredientInventory: (raw.ingredient_inventory as GameState["ingredientInventory"]) ?? [],
    consumables: (raw.consumables as GameState["consumables"]) ?? [],
    kills: (raw.kills as number) ?? 0,
    causeOfDeath: (raw.cause_of_death as string | null) ?? null,
  };
}

export { normalizeState };

export const useGameStore = create<GameStore>()(
  devtools(
    (set) => ({
      runId: null,
      playerClass: null,
      status: null,
      state: null,

      setRun: (run) =>
        set({
          runId: run.id,
          playerClass: run.playerClass,
          status: run.status,
          state: run.state ?? defaultGameState,
        }),

      updateState: (patch) =>
        set((s) => ({
          state: s.state ? { ...s.state, ...patch } : { ...defaultGameState, ...patch },
        })),

      setStatus: (status) => set({ status }),

      resetRun: () =>
        set({ runId: null, playerClass: null, status: null, state: null }),

      syncFromServer: async (runId: string) => {
        try {
          const res = await runsApi.getState(runId);
          const normalized = normalizeState(res.state as unknown as Record<string, unknown>);
          set({
            runId: res.id,
            playerClass: res.player_class,
            status: res.status as RunStatus,
            state: normalized,
          });
        } catch {
          // If fetch fails (e.g. run deleted), reset
          set({ runId: null, playerClass: null, status: null, state: null });
        }
      },
    }),
    { name: "GameStore" }
  )
);
