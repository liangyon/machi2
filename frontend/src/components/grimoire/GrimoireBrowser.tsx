"use client";

import { useEffect, useState } from "react";
import { grimoireApi } from "@/lib/api";
import type { GrimoireEntry } from "@/types/game";

export function GrimoireBrowser() {
  const [spells, setSpells] = useState<GrimoireEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    grimoireApi
      .list({ page, pageSize: 20, name: search || undefined })
      .then((res) => {
        setSpells(res.spells);
        setTotal(res.total);
      })
      .finally(() => setLoading(false));
  }, [page, search]);

  return (
    <div className="p-4 space-y-3">
      <h2 className="text-lg font-bold text-yellow-300">📖 Grimoire</h2>
      <input
        type="text"
        placeholder="Search spells…"
        value={search}
        onChange={(e) => { setSearch(e.target.value); setPage(1); }}
        className="w-full px-3 py-1.5 rounded bg-gray-800 border border-gray-600 text-sm focus:outline-none focus:border-yellow-400"
      />
      {loading ? (
        <p className="text-gray-500 text-sm">Loading…</p>
      ) : (
        <ul className="space-y-2">
          {spells.map((s) => (
            <li key={`${s.ingredientKey}:${s.variantIndex}`} className="p-2 rounded bg-gray-800 text-sm">
              <div className="font-semibold text-yellow-200">{s.spellName}</div>
              {s.flavorText && <div className="text-gray-400 italic text-xs">{s.flavorText}</div>}
              <div className="text-gray-500 text-xs mt-1">
                {s.discoveredBy && <>Discovered by {s.discoveredBy} · </>}
                Luck ≥ {s.luckThreshold}
              </div>
            </li>
          ))}
        </ul>
      )}
      <div className="flex gap-2 text-sm">
        <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1} className="px-2 py-1 rounded bg-gray-700 disabled:opacity-40">←</button>
        <span className="text-gray-400">Page {page} · {total} spells</span>
        <button onClick={() => setPage((p) => p + 1)} disabled={page * 20 >= total} className="px-2 py-1 rounded bg-gray-700 disabled:opacity-40">→</button>
      </div>
    </div>
  );
}
