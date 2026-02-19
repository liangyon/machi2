"use client";

import { useGameStore } from "@/stores/useGameStore";

export function HUD() {
  const state = useGameStore((s) => s.state);
  const playerClass = useGameStore((s) => s.playerClass);

  if (!state) return null;

  const dangerColor =
    state.dangerMeter > 85 ? "text-red-500" :
    state.dangerMeter > 60 ? "text-orange-400" :
    state.dangerMeter > 30 ? "text-yellow-400" :
    "text-green-400";

  return (
    <div className="flex flex-wrap gap-x-4 gap-y-1 items-center px-3 py-2 bg-gray-900 border-b border-gray-700 text-sm font-mono">
      {/* HP bar */}
      <span className="text-red-400">
        ❤️ {state.hp}/{state.maxHp}
      </span>
      {/* Mana bar */}
      <span className="text-blue-400">
        💧 {state.mana}/{state.maxMana}
      </span>
      {/* Divider */}
      <span className="text-gray-600">|</span>
      {/* Attack */}
      <span className="text-orange-300">⚔️ ATK {state.attack}</span>
      {/* Defense */}
      <span className="text-cyan-300">🛡️ DEF {state.defense}</span>
      {/* Speed */}
      <span className="text-yellow-300">⚡ SPD {state.speed}</span>
      {/* Class-specific stat */}
      {playerClass === "mage" ? (
        <span className="text-purple-300">✨ ARC {state.arcaneAffinity}</span>
      ) : (
        <span className="text-red-300">💪 STR {state.strength}</span>
      )}
      {/* Divider */}
      <span className="text-gray-600">|</span>
      {/* Gold */}
      <span className="text-yellow-500">🪙 {state.gold}</span>
      {/* Floor */}
      <span className="text-purple-400">🏰 F{state.floor}</span>
      {/* Danger meter */}
      <span className={dangerColor}>🔥 {state.dangerMeter}%</span>
      {/* XP / Level */}
      <span className="text-green-400">
        ⭐ Lv.{state.level}
      </span>
      {/* Unspent stat points indicator */}
      {state.unspentStatPoints > 0 && (
        <span className="text-yellow-300 animate-pulse font-bold">
          +{state.unspentStatPoints} pts
        </span>
      )}
    </div>
  );
}
