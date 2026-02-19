import { create } from "zustand";
import { devtools, persist } from "zustand/middleware";
import type { Spell } from "@/types/game";

const MAX_BANKED = 5;
const MAX_STARTING = 3;

interface LegacyStore {
  // Up to 5 banked spells from previous runs
  bankedSpells: Spell[];

  // Up to 3 selected for the current run start
  selectedStartingSpells: Spell[];

  // Actions
  bankSpell: (spell: Spell) => void;
  removeFromBank: (ingredientKey: string, variantIndex?: number) => void;
  selectStartingSpell: (spell: Spell) => void;
  deselectStartingSpell: (ingredientKey: string, variantIndex?: number) => void;
  clearStartingSelection: () => void;
}

export const useLegacyStore = create<LegacyStore>()(
  devtools(
    persist(
      (set, get) => ({
        bankedSpells: [],
        selectedStartingSpells: [],

        bankSpell: (spell) =>
          set((s) => {
            if (s.bankedSpells.length >= MAX_BANKED) return s;
            const exists = s.bankedSpells.some(
              (b) =>
                b.ingredientKey === spell.ingredientKey &&
                b.variantIndex === spell.variantIndex
            );
            if (exists) return s;
            return { bankedSpells: [...s.bankedSpells, spell] };
          }),

        removeFromBank: (ingredientKey, variantIndex = 0) =>
          set((s) => ({
            bankedSpells: s.bankedSpells.filter(
              (b) =>
                !(b.ingredientKey === ingredientKey && b.variantIndex === variantIndex)
            ),
          })),

        selectStartingSpell: (spell) =>
          set((s) => {
            if (s.selectedStartingSpells.length >= MAX_STARTING) return s;
            const exists = s.selectedStartingSpells.some(
              (b) =>
                b.ingredientKey === spell.ingredientKey &&
                b.variantIndex === spell.variantIndex
            );
            if (exists) return s;
            return {
              selectedStartingSpells: [...s.selectedStartingSpells, spell],
            };
          }),

        deselectStartingSpell: (ingredientKey, variantIndex = 0) =>
          set((s) => ({
            selectedStartingSpells: s.selectedStartingSpells.filter(
              (b) =>
                !(b.ingredientKey === ingredientKey && b.variantIndex === variantIndex)
            ),
          })),

        clearStartingSelection: () => set({ selectedStartingSpells: [] }),
      }),
      { name: "arcane-depths-legacy" }
    ),
    { name: "LegacyStore" }
  )
);
