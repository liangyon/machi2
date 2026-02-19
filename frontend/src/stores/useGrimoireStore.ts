import { create } from "zustand";
import { devtools } from "zustand/middleware";
import type { GrimoireEntry } from "@/types/game";

interface GrimoireStore {
  // Session-cached grimoire entries keyed by `${ingredientKey}:${variantIndex}`
  entries: Record<string, GrimoireEntry>;

  // Actions
  addEntry: (entry: GrimoireEntry) => void;
  addEntries: (entries: GrimoireEntry[]) => void;
  getEntry: (ingredientKey: string, variantIndex?: number) => GrimoireEntry | undefined;
  clearCache: () => void;
}

export const useGrimoireStore = create<GrimoireStore>()(
  devtools(
    (set, get) => ({
      entries: {},

      addEntry: (entry) =>
        set((s) => ({
          entries: {
            ...s.entries,
            [`${entry.ingredientKey}:${entry.variantIndex}`]: entry,
          },
        })),

      addEntries: (entries) =>
        set((s) => {
          const next = { ...s.entries };
          for (const e of entries) {
            next[`${e.ingredientKey}:${e.variantIndex}`] = e;
          }
          return { entries: next };
        }),

      getEntry: (ingredientKey, variantIndex = 0) =>
        get().entries[`${ingredientKey}:${variantIndex}`],

      clearCache: () => set({ entries: {} }),
    }),
    { name: "GrimoireStore" }
  )
);
