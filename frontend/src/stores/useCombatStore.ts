import { create } from "zustand";
import { devtools } from "zustand/middleware";
import type { Enemy, TurnLogEntry, StatusEffect } from "@/types/game";

interface CombatStore {
  // Enemy
  enemy: Enemy | null;

  // Turn log
  turnLog: TurnLogEntry[];

  // SSE narration streaming
  narrationBuffer: string;
  isStreaming: boolean;

  // Status effects
  playerStatusEffects: StatusEffect[];
  enemyStatusEffects: StatusEffect[];

  // Actions
  setEnemy: (enemy: Enemy) => void;
  updateEnemyHp: (hp: number) => void;
  appendNarration: (token: string) => void;
  clearNarration: () => void;
  setStreaming: (streaming: boolean) => void;
  addTurnLogEntry: (entry: TurnLogEntry) => void;
  setPlayerStatusEffects: (effects: StatusEffect[]) => void;
  setEnemyStatusEffects: (effects: StatusEffect[]) => void;
  resetCombat: () => void;
}

export const useCombatStore = create<CombatStore>()(
  devtools(
    (set) => ({
      enemy: null,
      turnLog: [],
      narrationBuffer: "",
      isStreaming: false,
      playerStatusEffects: [],
      enemyStatusEffects: [],

      setEnemy: (enemy) => set({ enemy }),

      updateEnemyHp: (hp) =>
        set((s) => ({
          enemy: s.enemy ? { ...s.enemy, hp } : null,
        })),

      appendNarration: (token) =>
        set((s) => ({ narrationBuffer: s.narrationBuffer + token })),

      clearNarration: () => set({ narrationBuffer: "" }),

      setStreaming: (isStreaming) => set({ isStreaming }),

      addTurnLogEntry: (entry) =>
        set((s) => ({ turnLog: [...s.turnLog, entry] })),

      setPlayerStatusEffects: (playerStatusEffects) =>
        set({ playerStatusEffects }),

      setEnemyStatusEffects: (enemyStatusEffects) =>
        set({ enemyStatusEffects }),

      resetCombat: () =>
        set({
          enemy: null,
          turnLog: [],
          narrationBuffer: "",
          isStreaming: false,
          playerStatusEffects: [],
          enemyStatusEffects: [],
        }),
    }),
    { name: "CombatStore" }
  )
);
