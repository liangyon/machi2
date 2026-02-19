"use client";

import { useState, useEffect, useCallback } from "react";
import { HUD } from "@/components/hud/HUD";
import { StatusBar } from "@/components/hud/StatusBar";
import { NarrativeLog } from "@/components/narrative/NarrativeLog";
import { ActionMenu, type GameMode, type Action } from "@/components/combat/ActionMenu";
import { FloorMap } from "@/components/map/FloorMap";
import { useGameStore, normalizeState } from "@/stores/useGameStore";
import { useCombatStore } from "@/stores/useCombatStore";
import { runsApi } from "@/lib/api";
import { streamSSE } from "@/lib/sse";
import type { EnemyState, ShrineChoice } from "@/types/game";

// ─── Class Selection Modal ────────────────────────────────────────────────────

function ClassSelectModal({
  onSelect,
  loading,
}: {
  onSelect: (cls: "knight" | "mage") => void;
  loading: boolean;
}) {
  return (
    <main className="min-h-screen bg-gray-950 text-gray-100 flex flex-col items-center justify-center gap-8 p-6">
      <h1 className="text-4xl font-bold text-purple-300 tracking-wide">⚔️ Arcane Depths</h1>
      <p className="text-gray-400 text-lg">Choose your class to begin</p>
      <div className="flex gap-6">
        <button
          onClick={() => onSelect("knight")}
          disabled={loading}
          className="flex flex-col items-center gap-3 px-8 py-6 rounded-xl bg-gray-800 border-2 border-orange-600 hover:border-orange-400 hover:bg-gray-700 disabled:opacity-50 transition-all w-48"
        >
          <span className="text-5xl">🛡️</span>
          <span className="text-xl font-bold text-orange-300">Knight</span>
          <span className="text-xs text-gray-400 text-center">High attack & defense. Physical powerhouse.</span>
          <div className="text-xs text-gray-500 space-y-0.5 text-left w-full mt-1">
            <div>ATK 12 · DEF 8 · SPD 8</div>
            <div>STR 15 · Mana 30</div>
          </div>
        </button>
        <button
          onClick={() => onSelect("mage")}
          disabled={loading}
          className="flex flex-col items-center gap-3 px-8 py-6 rounded-xl bg-gray-800 border-2 border-purple-600 hover:border-purple-400 hover:bg-gray-700 disabled:opacity-50 transition-all w-48"
        >
          <span className="text-5xl">✨</span>
          <span className="text-xl font-bold text-purple-300">Mage</span>
          <span className="text-xs text-gray-400 text-center">Arcane spells & status effects. Glass cannon.</span>
          <div className="text-xs text-gray-500 space-y-0.5 text-left w-full mt-1">
            <div>ATK 7 · DEF 3 · SPD 9</div>
            <div>ARC 15 · Mana 80</div>
          </div>
        </button>
      </div>
      {loading && <p className="text-purple-400 animate-pulse">Entering the dungeon…</p>}
    </main>
  );
}

// ─── Death Screen ─────────────────────────────────────────────────────────────

function DeathScreen({ onRestart }: { onRestart: () => void }) {
  const state = useGameStore((s) => s.state);
  const playerClass = useGameStore((s) => s.playerClass);

  return (
    <main className="min-h-screen bg-gray-950 text-gray-100 flex flex-col items-center justify-center gap-6 p-6">
      <div className="text-6xl">💀</div>
      <h1 className="text-3xl font-bold text-red-400">You Have Fallen</h1>
      {state?.causeOfDeath && (
        <p className="text-gray-400 italic">{state.causeOfDeath}</p>
      )}
      <div className="bg-gray-900 rounded-xl p-6 w-full max-w-sm space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-400">Class</span>
          <span className="capitalize">{playerClass}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-400">Floor Reached</span>
          <span>Floor {state?.floor ?? 1}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-400">Enemies Slain</span>
          <span>{state?.kills ?? 0}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-400">Gold Earned</span>
          <span>🪙 {state?.gold ?? 0}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-400">Level Reached</span>
          <span>Lv. {state?.level ?? 1}</span>
        </div>
      </div>
      <button
        onClick={onRestart}
        className="px-8 py-3 rounded-lg bg-red-800 hover:bg-red-700 font-semibold text-lg transition-colors"
      >
        🔄 Start New Run
      </button>
    </main>
  );
}

// ─── Victory Screen ───────────────────────────────────────────────────────────

function VictoryScreen({ onRestart }: { onRestart: () => void }) {
  const state = useGameStore((s) => s.state);
  const playerClass = useGameStore((s) => s.playerClass);

  return (
    <main className="min-h-screen bg-gray-950 text-gray-100 flex flex-col items-center justify-center gap-6 p-6">
      <div className="text-6xl">🏆</div>
      <h1 className="text-3xl font-bold text-yellow-300">Victory!</h1>
      <p className="text-gray-400">You have conquered the Arcane Depths.</p>
      <div className="bg-gray-900 rounded-xl p-6 w-full max-w-sm space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-400">Class</span>
          <span className="capitalize">{playerClass}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-400">Enemies Slain</span>
          <span>{state?.kills ?? 0}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-400">Gold Earned</span>
          <span>🪙 {state?.gold ?? 0}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-400">Final Level</span>
          <span>Lv. {state?.level ?? 1}</span>
        </div>
      </div>
      <button
        onClick={onRestart}
        className="px-8 py-3 rounded-lg bg-yellow-700 hover:bg-yellow-600 font-semibold text-lg transition-colors"
      >
        🔄 Start New Run
      </button>
    </main>
  );
}

// ─── Enemy Panel ──────────────────────────────────────────────────────────────

function EnemyPanel({ enemy }: { enemy: EnemyState }) {
  const hpPct = Math.max(0, Math.min(100, (enemy.hp / enemy.max_hp) * 100));
  const barColor = hpPct > 50 ? "bg-green-500" : hpPct > 25 ? "bg-yellow-500" : "bg-red-500";

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg p-3 mx-3 mb-2">
      <div className="flex justify-between items-center mb-1">
        <span className="font-bold text-red-300">👹 {enemy.name}</span>
        <span className="text-sm text-gray-400">{enemy.hp}/{enemy.max_hp} HP</span>
      </div>
      <div className="w-full bg-gray-700 rounded-full h-2">
        <div
          className={`${barColor} h-2 rounded-full transition-all duration-300`}
          style={{ width: `${hpPct}%` }}
        />
      </div>
      {enemy.active_status_effects.length > 0 && (
        <div className="flex gap-1 mt-1 flex-wrap">
          {enemy.active_status_effects.map((eff, i) => (
            <span key={i} className="text-xs bg-gray-700 px-1 rounded" title={eff.description}>
              {eff.emoji} {eff.name}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Loot Panel ───────────────────────────────────────────────────────────────

function LootPanel({ loot, onContinue }: { loot: { name: string; tier: string; quantity: number }[]; onContinue: () => void }) {
  return (
    <div className="bg-gray-800 border border-yellow-700 rounded-lg p-3 mx-3 mb-2">
      <div className="font-bold text-yellow-300 mb-2">📦 Chest Found!</div>
      <div className="space-y-1">
        {loot.map((item, i) => (
          <div key={i} className="flex justify-between text-sm">
            <span>{item.name}</span>
            <span className="text-gray-400">×{item.quantity} <span className="text-xs text-gray-500">({item.tier})</span></span>
          </div>
        ))}
      </div>
      <button
        onClick={onContinue}
        className="mt-2 w-full py-1 rounded bg-gray-700 hover:bg-gray-600 text-sm transition-colors"
      >
        Continue →
      </button>
    </div>
  );
}

// ─── Shop Panel ───────────────────────────────────────────────────────────────

function ShopPanel({ items, onClose }: { items: unknown[]; onClose: () => void }) {
  return (
    <div className="bg-gray-800 border border-green-700 rounded-lg p-3 mx-3 mb-2">
      <div className="font-bold text-green-300 mb-2">🛒 Merchant&apos;s Wares</div>
      <div className="space-y-1 max-h-32 overflow-y-auto">
        {(items as { name: string; price: number; type: string; tier: string }[]).map((item, i) => (
          <div key={i} className="flex justify-between text-sm">
            <span>{item.name} <span className="text-xs text-gray-500">({item.tier})</span></span>
            <span className="text-yellow-400">🪙 {item.price}</span>
          </div>
        ))}
      </div>
      <button
        onClick={onClose}
        className="mt-2 w-full py-1 rounded bg-gray-700 hover:bg-gray-600 text-sm transition-colors"
      >
        Leave Shop →
      </button>
    </div>
  );
}

// ─── Main Game Page ───────────────────────────────────────────────────────────

export default function GamePage() {
  const runId = useGameStore((s) => s.runId);
  const status = useGameStore((s) => s.status);
  const state = useGameStore((s) => s.state);
  const setRun = useGameStore((s) => s.setRun);
  const updateState = useGameStore((s) => s.updateState);
  const setStatus = useGameStore((s) => s.setStatus);
  const resetRun = useGameStore((s) => s.resetRun);

  const enemy = useCombatStore((s) => s.enemy);
  const setEnemy = useCombatStore((s) => s.setEnemy);
  const updateEnemyHp = useCombatStore((s) => s.updateEnemyHp);
  const setEnemyStatusEffects = useCombatStore((s) => s.setEnemyStatusEffects);
  const setPlayerStatusEffects = useCombatStore((s) => s.setPlayerStatusEffects);
  const resetCombat = useCombatStore((s) => s.resetCombat);
  const appendNarration = useCombatStore((s) => s.appendNarration);
  const clearNarration = useCombatStore((s) => s.clearNarration);
  const setStreaming = useCombatStore((s) => s.setStreaming);
  const isStreaming = useCombatStore((s) => s.isStreaming);

  const [gameMode, setGameMode] = useState<GameMode>("exploring");
  const [starting, setStarting] = useState(false);
  const [shrineChoices, setShrineChoices] = useState<ShrineChoice[]>([]);
  const [loot, setLoot] = useState<{ name: string; tier: string; quantity: number }[] | null>(null);
  const [shopItems, setShopItems] = useState<unknown[] | null>(null);

  // Rehydrate from current_enemy in state on load
  useEffect(() => {
    if (state?.currentEnemy && !enemy) {
      setEnemy({
        name: state.currentEnemy.name,
        hp: state.currentEnemy.hp,
        maxHp: state.currentEnemy.max_hp,
        speed: state.currentEnemy.speed,
        activeStatusEffects: state.currentEnemy.active_status_effects,
      });
      setGameMode("combat");
    }
  }, [state?.currentEnemy, enemy, setEnemy]);

  const handleStartRun = async (playerClass: "knight" | "mage") => {
    setStarting(true);
    try {
      const res = await runsApi.start(playerClass);
      const normalized = normalizeState(res.state as unknown as Record<string, unknown>);
      setRun({
        id: res.run_id,
        playerClass,
        state: normalized,
        floor: normalized.floor,
        status: "active",
      });
      resetCombat();
      setGameMode("exploring");
      clearNarration();
      appendNarration(`Welcome, ${playerClass === "mage" ? "Arcane Mage" : "Iron Knight"}. The dungeon awaits. Explore to begin.`);
    } finally {
      setStarting(false);
    }
  };

  const handleRestart = useCallback(() => {
    resetRun();
    resetCombat();
    setGameMode("exploring");
    setShrineChoices([]);
    setLoot(null);
    setShopItems(null);
    clearNarration();
  }, [resetRun, resetCombat, clearNarration]);

  const handleAction = useCallback(async (action: Action) => {
    if (!runId || isStreaming) return;

    // ── Explore ──────────────────────────────────────────────────────────
    if (action === "explore") {
      try {
        const res = await runsApi.explore(runId);
        clearNarration();
        appendNarration(res.room);
        updateState({ dangerMeter: res.danger_meter, actionCount: res.action_count });

        if (res.event_type === "enemy" && res.enemy) {
          const e = res.enemy;
          setEnemy({
            name: e.name,
            hp: e.hp,
            maxHp: e.max_hp,
            speed: e.speed,
            activeStatusEffects: [],
          });
          setGameMode("combat");
          appendNarration(`\n\n⚔️ A ${e.name} appears! (${e.hp} HP)`);
        } else if (res.event_type === "chest" && res.loot) {
          setLoot(res.loot);
          setGameMode("chest");
        } else if (res.event_type === "shrine" && res.shrine_choices) {
          setShrineChoices(res.shrine_choices);
          setGameMode("shrine");
        } else if (res.event_type === "shop" && res.shop_items) {
          setShopItems(res.shop_items);
          setGameMode("shop");
        } else {
          setGameMode("exploring");
        }
      } catch (err) {
        appendNarration("\n[Error exploring — try again]");
      }
      return;
    }

    // ── Challenge Boss ────────────────────────────────────────────────────
    if (action === "challenge_boss") {
      try {
        const res = await runsApi.boss(runId);
        const b = res.boss;
        setEnemy({
          name: b.name,
          hp: b.hp,
          maxHp: b.max_hp,
          speed: b.speed,
          activeStatusEffects: [],
        });
        setGameMode("combat");
        clearNarration();
        appendNarration(
          res.is_final_boss
            ? `💀 THE FINAL BOSS: ${b.name} (${b.hp} HP). This is it.`
            : `👹 MINI-BOSS: ${b.name} (${b.hp} HP). Prepare yourself!`
        );
      } catch {
        appendNarration("\n[Error initiating boss — try again]");
      }
      return;
    }

    // ── Shrine choice ─────────────────────────────────────────────────────
    if (action.startsWith("choose_shrine_")) {
      const idx = parseInt(action.slice(-1));
      try {
        const res = await runsApi.chooseShrineOutcome(runId, idx);
        const normalized = normalizeState(res.state);
        updateState(normalized);
        clearNarration();
        const icon = res.outcome === "buff" ? "✨" : res.outcome === "curse" ? "💀" : "🌀";
        appendNarration(`${icon} ${res.description}`);
        setGameMode("exploring");
        setShrineChoices([]);
      } catch {
        appendNarration("\n[Error choosing shrine — try again]");
      }
      return;
    }

    // ── Combat actions ────────────────────────────────────────────────────
    if (gameMode === "combat") {
      const actionMap: Record<string, string> = {
        basic_attack: "basic_attack",
        heavy_attack: "heavy_attack",
        cast_spell: "cast_spell",
        defend: "defend",
        flee: "flee",
        use_item: "use_item",
      };
      const actionType = actionMap[action] ?? "basic_attack";

      clearNarration();
      setStreaming(true);

      let resultData: Record<string, unknown> | null = null;

      await streamSSE(
        runsApi.combatActionPath(runId),
        { type: actionType },
        (token) => appendNarration(token),
        () => setStreaming(false),
        () => setStreaming(false),
        (data) => {
          // Capture the result payload from the SSE stream
          if (data.result) {
            resultData = data.result as Record<string, unknown>;
          }
        }
      );

      // Process result after stream completes
      if (resultData) {
        const r = resultData as {
          player_hp: number;
          player_mana: number;
          player_status_effects: unknown[];
          enemy_hp: number;
          enemy_status_effects: unknown[];
          player_won: boolean;
          player_died: boolean;
          xp_gained: number;
          gold_gained: number;
          run_status: string;
          leveled_up: boolean;
          level_up_info: { new_level: number; unspent_stat_points: number } | null;
          fled?: boolean;
          state: Record<string, unknown>;
        };

        if (r.fled) {
          resetCombat();
          setGameMode("exploring");
          return;
        }

        // Update enemy HP in combat store
        updateEnemyHp(r.enemy_hp);
        setEnemyStatusEffects(r.enemy_status_effects as never[]);
        setPlayerStatusEffects(r.player_status_effects as never[]);

        // Sync full state from result
        const normalized = normalizeState(r.state);
        updateState(normalized);

        if (r.player_won) {
          resetCombat();
          setGameMode("exploring");
          if (r.leveled_up && r.level_up_info) {
            appendNarration(`\n\n🎉 LEVEL UP! You are now level ${r.level_up_info.new_level}! (+${r.level_up_info.unspent_stat_points} stat points)`);
          }
          if (r.xp_gained > 0) {
            appendNarration(`\n+${r.xp_gained} XP, +${r.gold_gained} gold`);
          }
        } else if (r.player_died || r.run_status === "dead") {
          setStatus("dead");
          resetCombat();
          setGameMode("dead");
        }
      }
      return;
    }

    // ── Shop / chest continue ─────────────────────────────────────────────
    if (action === "visit_shop") {
      // Shop is display-only for now; just show the panel
      return;
    }
  }, [
    runId, isStreaming, gameMode, clearNarration, appendNarration, updateState,
    setEnemy, setGameMode, setStreaming, updateEnemyHp, setEnemyStatusEffects,
    setPlayerStatusEffects, resetCombat, setStatus,
  ]);

  // ── Render: no run yet → class select ────────────────────────────────────
  if (!runId || status === null) {
    return <ClassSelectModal onSelect={handleStartRun} loading={starting} />;
  }

  // ── Render: dead ─────────────────────────────────────────────────────────
  if (status === "dead") {
    return <DeathScreen onRestart={handleRestart} />;
  }

  // ── Render: victory ───────────────────────────────────────────────────────
  if (status === "victory") {
    return <VictoryScreen onRestart={handleRestart} />;
  }

  // ── Render: active game ───────────────────────────────────────────────────
  return (
    <main className="h-screen flex flex-col bg-gray-950 text-gray-100 overflow-hidden">
      <HUD />
      <StatusBar />
      <div className="flex flex-1 min-h-0">
        {/* Left sidebar */}
        <aside className="w-48 flex-shrink-0 border-r border-gray-800 p-3 overflow-y-auto">
          <FloorMap />
        </aside>

        {/* Main content */}
        <div className="flex flex-col flex-1 min-h-0">
          {/* Enemy panel (combat mode) */}
          {gameMode === "combat" && enemy && (
            <EnemyPanel enemy={{
              name: enemy.name,
              hp: enemy.hp,
              max_hp: enemy.maxHp,
              speed: enemy.speed,
              attack: state?.currentEnemy?.attack ?? 0,
              defense: state?.currentEnemy?.defense ?? 0,
              xp: state?.currentEnemy?.xp ?? 0,
              gold_min: state?.currentEnemy?.gold_min ?? 0,
              gold_max: state?.currentEnemy?.gold_max ?? 0,
              active_status_effects: enemy.activeStatusEffects,
            }} />
          )}

          {/* Loot panel */}
          {gameMode === "chest" && loot && (
            <LootPanel
              loot={loot}
              onContinue={() => { setLoot(null); setGameMode("exploring"); }}
            />
          )}

          {/* Shop panel */}
          {gameMode === "shop" && shopItems && (
            <ShopPanel
              items={shopItems}
              onClose={() => { setShopItems(null); setGameMode("exploring"); }}
            />
          )}

          <NarrativeLog />

          <ActionMenu
            mode={gameMode}
            onAction={handleAction}
            disabled={isStreaming}
            shrineChoices={shrineChoices}
            unspentStatPoints={state?.unspentStatPoints}
          />
        </div>
      </div>
    </main>
  );
}
