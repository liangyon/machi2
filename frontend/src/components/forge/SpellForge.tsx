"use client";

import { useState } from "react";
import { runsApi } from "@/lib/api";

interface SpellForgeProps {
  runId: string;
  availableIngredients: { id: string; name: string; tier: number }[];
  onSpellForged?: (spell: unknown) => void;
}

export function SpellForge({ runId, availableIngredients, onSpellForged }: SpellForgeProps) {
  const [selected, setSelected] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const toggle = (id: string) => {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const handleForge = async () => {
    if (selected.length === 0) return;
    setLoading(true);
    try {
      const data = await runsApi.forge(runId, selected);
      onSpellForged?.(data.spell);
      setSelected([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 bg-gray-900 rounded-lg space-y-3">
      <h2 className="text-lg font-bold text-purple-300">✨ Spell Forge</h2>
      <div className="flex flex-wrap gap-2">
        {availableIngredients.map((ing) => (
          <button
            key={ing.id}
            onClick={() => toggle(ing.id)}
            className={`px-2 py-1 rounded text-xs border transition-colors ${
              selected.includes(ing.id)
                ? "bg-purple-700 border-purple-400 text-white"
                : "bg-gray-800 border-gray-600 text-gray-300 hover:border-purple-500"
            }`}
          >
            {ing.name} <span className="opacity-60">T{ing.tier}</span>
          </button>
        ))}
      </div>
      <button
        onClick={handleForge}
        disabled={selected.length === 0 || loading}
        className="w-full py-2 rounded bg-purple-700 hover:bg-purple-600 disabled:opacity-40 disabled:cursor-not-allowed font-semibold transition-colors"
      >
        {loading ? "Forging…" : "Forge Spell"}
      </button>
    </div>
  );
}
