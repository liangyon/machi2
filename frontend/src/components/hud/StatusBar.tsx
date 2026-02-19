"use client";

import { useCombatStore } from "@/stores/useCombatStore";

export function StatusBar() {
  const playerEffects = useCombatStore((s) => s.playerStatusEffects);
  const enemyEffects = useCombatStore((s) => s.enemyStatusEffects);

  if (playerEffects.length === 0 && enemyEffects.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2 px-3 py-2 bg-gray-800 text-xs font-mono border-b border-gray-700">
      {playerEffects.map((e) => (
        <span key={e.name} className="text-green-300" title={e.description}>
          {e.emoji} {e.name} {e.turnsRemaining}t
        </span>
      ))}
      {enemyEffects.map((e) => (
        <span key={e.name} className="text-red-300" title={e.description}>
          {e.emoji} {e.name} {e.turnsRemaining}t
        </span>
      ))}
    </div>
  );
}
