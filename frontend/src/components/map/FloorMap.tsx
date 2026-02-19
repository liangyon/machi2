"use client";

import { useGameStore } from "@/stores/useGameStore";

// Simple visual floor map — explored rooms, danger level
export function FloorMap() {
  const floor = useGameStore((s) => s.state?.floor ?? 1);
  const dangerMeter = useGameStore((s) => s.state?.dangerMeter ?? 0);

  return (
    <div className="p-3 bg-gray-900 rounded-lg text-xs font-mono space-y-1">
      <div className="text-purple-300 font-bold">🗺️ Floor {floor}</div>
      <div className="flex gap-1">
        {Array.from({ length: 10 }).map((_, i) => (
          <div
            key={i}
            className={`w-5 h-5 rounded-sm border ${
              i < dangerMeter / 10
                ? "bg-orange-600 border-orange-400"
                : "bg-gray-800 border-gray-600"
            }`}
          />
        ))}
      </div>
      <div className="text-gray-500">Danger: {dangerMeter}/100</div>
    </div>
  );
}
