"use client";

import { useLegacyStore } from "@/stores/useLegacyStore";

export function LegacySpellbook() {
  const bankedSpells = useLegacyStore((s) => s.bankedSpells);
  const selected = useLegacyStore((s) => s.selectedStartingSpells);
  const select = useLegacyStore((s) => s.selectStartingSpell);
  const deselect = useLegacyStore((s) => s.deselectStartingSpell);

  return (
    <div className="p-4 space-y-3">
      <h2 className="text-lg font-bold text-cyan-300">📚 Legacy Spellbook</h2>
      <p className="text-xs text-gray-400">Select up to 3 spells to bring into your next run.</p>
      {bankedSpells.length === 0 ? (
        <p className="text-gray-500 text-sm">No banked spells yet.</p>
      ) : (
        <ul className="space-y-2">
          {bankedSpells.map((spell) => {
            const isSelected = selected.some(
              (s) => s.ingredientKey === spell.ingredientKey && s.variantIndex === spell.variantIndex
            );
            return (
              <li
                key={`${spell.ingredientKey}:${spell.variantIndex}`}
                className={`p-2 rounded border text-sm cursor-pointer transition-colors ${
                  isSelected
                    ? "bg-cyan-900 border-cyan-400"
                    : "bg-gray-800 border-gray-600 hover:border-cyan-500"
                }`}
                onClick={() =>
                  isSelected
                    ? deselect(spell.ingredientKey, spell.variantIndex)
                    : select(spell)
                }
              >
                <div className="font-semibold text-cyan-200">{spell.spellName}</div>
                {spell.flavorText && (
                  <div className="text-gray-400 italic text-xs">{spell.flavorText}</div>
                )}
              </li>
            );
          })}
        </ul>
      )}
      <p className="text-xs text-gray-500">{selected.length}/3 selected</p>
    </div>
  );
}
