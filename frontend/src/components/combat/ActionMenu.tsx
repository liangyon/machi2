"use client";

export type GameMode = "exploring" | "combat" | "shrine" | "shop" | "chest" | "victory" | "dead";

export type Action =
  | "explore"
  | "cast_spell"
  | "basic_attack"
  | "heavy_attack"
  | "use_item"
  | "defend"
  | "flee"
  | "open_chest"
  | "visit_shop"
  | "challenge_boss"
  | "choose_shrine_0"
  | "choose_shrine_1"
  | "choose_shrine_2";

interface ActionMenuProps {
  mode: GameMode;
  onAction: (action: Action) => void;
  disabled?: boolean;
  shrineChoices?: { id: number; flavor: string }[];
  unspentStatPoints?: number;
}

const ACTION_LABELS: Record<Action, string> = {
  explore: "🗺️ Explore",
  cast_spell: "✨ Cast Spell",
  basic_attack: "⚔️ Attack",
  heavy_attack: "💥 Heavy Attack",
  use_item: "🎒 Use Item",
  defend: "🛡️ Defend",
  flee: "💨 Flee",
  open_chest: "📦 Open Chest",
  visit_shop: "🛒 Visit Shop",
  challenge_boss: "💀 Challenge Boss",
  choose_shrine_0: "🔮 Choice I",
  choose_shrine_1: "🔮 Choice II",
  choose_shrine_2: "🔮 Choice III",
};

const ACTIONS_BY_MODE: Record<GameMode, Action[]> = {
  exploring: ["explore", "cast_spell", "use_item", "challenge_boss"],
  combat:    ["basic_attack", "heavy_attack", "cast_spell", "use_item", "defend", "flee"],
  shrine:    ["choose_shrine_0", "choose_shrine_1", "choose_shrine_2"],
  shop:      ["visit_shop", "explore"],
  chest:     ["explore"],
  victory:   [],
  dead:      [],
};

export function ActionMenu({ mode, onAction, disabled, shrineChoices, unspentStatPoints }: ActionMenuProps) {
  const actions = ACTIONS_BY_MODE[mode] ?? [];

  return (
    <div className="flex flex-col gap-2 p-3 bg-gray-900 border-t border-gray-700">
      {unspentStatPoints != null && unspentStatPoints > 0 && (
        <div className="text-yellow-400 text-xs font-semibold px-1">
          ⭐ {unspentStatPoints} unspent stat point{unspentStatPoints !== 1 ? "s" : ""} — visit stats to allocate
        </div>
      )}
      <div className="grid grid-cols-2 gap-2">
        {actions.map((action) => {
          // For shrine choices, show the flavor text if available
          let label = ACTION_LABELS[action];
          if (action.startsWith("choose_shrine_") && shrineChoices) {
            const idx = parseInt(action.slice(-1));
            if (shrineChoices[idx]) {
              label = `🔮 ${shrineChoices[idx].flavor.slice(0, 40)}…`;
            }
          }
          return (
            <button
              key={action}
              onClick={() => onAction(action)}
              disabled={disabled}
              className="px-3 py-2 rounded bg-gray-700 hover:bg-gray-600 disabled:opacity-40 disabled:cursor-not-allowed text-sm font-medium transition-colors text-left"
            >
              {label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
